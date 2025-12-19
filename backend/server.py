from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

# Import custom modules
from scraper import SHLScraper
from embeddings import GeminiEmbeddings
from vector_store import VectorStore
from rag_pipeline import RAGPipeline
from evaluation import EvaluationMetrics


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize components
scraper = SHLScraper()
embeddings = GeminiEmbeddings()
vector_store = VectorStore()
rag_pipeline = RAGPipeline(vector_store, embeddings)
evaluator = EvaluationMetrics()

# Create the main app without a prefix
app = FastAPI(title="SHL Assessment Recommendation System")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class RecommendRequest(BaseModel):
    query: str

class Assessment(BaseModel):
    name: str
    url: str
    description: str
    duration: int
    test_type: List[str]
    adaptive_support: str
    remote_support: str

class RecommendResponse(BaseModel):
    recommended_assessments: List[Assessment]

class ScrapeResponse(BaseModel):
    status: str
    message: str
    assessments_count: int

class EvaluateRequest(BaseModel):
    test_file_url: Optional[str] = None

class EvaluateResponse(BaseModel):
    mean_recall_at_5: float
    mean_recall_at_10: float
    total_queries: int
    message: str


# Health Check Endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Assessment Recommendation Endpoint
@api_router.post("/recommend", response_model=RecommendResponse)
async def recommend_assessments(request: RecommendRequest):
    try:
        logger.info(f"Recommendation request: {request.query}")
        
        # Check if vector store is populated
        if vector_store.count() == 0:
            logger.warning("Vector store is empty, triggering scraping")
            await scrape_and_index()
        
        # Get recommendations
        recommendations = await rag_pipeline.recommend(request.query, n_results=10)
        
        if not recommendations:
            raise HTTPException(status_code=404, detail="No assessments found")
        
        # Format response
        assessments = [
            Assessment(
                name=rec['name'],
                url=rec['url'],
                description=rec['description'],
                duration=int(rec['duration']),
                test_type=rec['test_type'],
                adaptive_support=rec['adaptive_support'],
                remote_support=rec['remote_support']
            )
            for rec in recommendations
        ]
        
        return RecommendResponse(recommended_assessments=assessments)
        
    except Exception as e:
        logger.error(f"Error in recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Scrape and Index Endpoint
@api_router.post("/scrape", response_model=ScrapeResponse)
async def scrape_assessments(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(scrape_and_index)
        return ScrapeResponse(
            status="started",
            message="Scraping and indexing started in background",
            assessments_count=0
        )
    except Exception as e:
        logger.error(f"Error starting scrape: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def scrape_and_index():
    """Scrape SHL catalog and index in vector store"""
    try:
        logger.info("Starting scraping and indexing process")
        
        # Scrape assessments
        assessments = scraper.scrape_catalog()
        
        if not assessments:
            logger.error("No assessments scraped")
            return
        
        # Save to MongoDB
        await save_assessments_to_db(assessments)
        
        # Generate embeddings
        logger.info("Generating embeddings")
        documents = [f"{a['name']} {a['description']} {' '.join(a['test_type'])}" for a in assessments]
        embeddings_list = await embeddings.get_embeddings_batch(documents)
        
        # Clear and add to vector store
        vector_store.clear()
        vector_store.add_assessments(assessments, embeddings_list)
        
        logger.info(f"Successfully indexed {len(assessments)} assessments")
        
    except Exception as e:
        logger.error(f"Error in scrape_and_index: {str(e)}")


async def save_assessments_to_db(assessments: List[dict]):
    """Save assessments to MongoDB"""
    try:
        # Clear existing assessments
        await db.assessments.delete_many({})
        
        # Insert new assessments
        if assessments:
            await db.assessments.insert_many(assessments)
            logger.info(f"Saved {len(assessments)} assessments to MongoDB")
    except Exception as e:
        logger.error(f"Error saving to MongoDB: {str(e)}")


# Evaluation Endpoint
@api_router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_system(request: EvaluateRequest):
    try:
        # Load test data
        if request.test_file_url:
            import requests
            import tempfile
            
            response = requests.get(request.test_file_url)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                tmp.write(response.content)
                test_data = evaluator.load_train_data(tmp.name)
        else:
            # Use default test data location
            test_data = evaluator.load_train_data("/app/data/test_data.xlsx")
        
        if not test_data:
            raise HTTPException(status_code=404, detail="Test data not found")
        
        # Run evaluation
        async def predict_wrapper(query):
            return await rag_pipeline.recommend(query, n_results=10)
        
        results = evaluator.evaluate_system(test_data, predict_wrapper)
        
        # Save results
        await db.evaluation_results.insert_one(results)
        
        return EvaluateResponse(
            mean_recall_at_5=results['mean_recall@5'],
            mean_recall_at_10=results['mean_recall@10'],
            total_queries=results['total_queries'],
            message="Evaluation completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Get Assessments from DB
@api_router.get("/assessments")
async def get_assessments():
    try:
        assessments = await db.assessments.find({}, {"_id": 0}).to_list(1000)
        return {"assessments": assessments, "count": len(assessments)}
    except Exception as e:
        logger.error(f"Error getting assessments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting SHL Assessment Recommendation System")
    
    # Check if vector store is empty and trigger scraping
    if vector_store.count() == 0:
        logger.info("Vector store is empty, starting initial scraping")
        import asyncio
        asyncio.create_task(scrape_and_index())


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
