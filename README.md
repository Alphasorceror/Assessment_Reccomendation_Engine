# Assessment Recommendation Engine

A comprehensive RAG (Retrieval-Augmented Generation) powered application that provides intelligent assessment recommendations using AI. The system combines web scraping, vector embeddings, and modern AI models to deliver accurate and contextual recommendations.

## 🌟 Features

- **Web Scraping**: Automated data collection from multiple sources
- **Vector Embeddings**: Uses advanced embedding models for semantic understanding
- **RAG Pipeline**: Retrieval-Augmented Generation for accurate, contextual responses
- **Vector Database**: ChromaDB for efficient similarity search
- **AI Integration**: Google Gemini API for intelligent recommendations
- **REST API**: FastAPI backend for scalable performance
- **Modern UI**: React-based frontend with responsive design
- **Evaluation Framework**: Built-in evaluation tools to assess recommendation quality

## 📋 Project Structure

```
Assessment_Recommendation_Engine/
├── backend/                 # Python FastAPI backend
│   ├── server.py           # Main API server
│   ├── rag_pipeline.py     # RAG implementation
│   ├── embeddings.py       # Embedding generation
│   ├── vector_store.py     # Vector database management
│   ├── scraper.py          # Web scraping utilities
│   ├── evaluation.py       # Evaluation metrics
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── pages/         # Main application pages
│   │   ├── components/    # Reusable React components
│   │   └── hooks/         # Custom React hooks
│   └── public/            # Static assets
├── data/
│   └── chroma/           # Vector store data
└── tests/                # Test suite
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn
- Google Gemini API key

### Backend Setup

1. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set up environment variables**
Create a `.env` file in the backend directory:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

3. **Start the API server**
```bash
python server.py
```
The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Start the development server**
```bash
npm start
```
The application will open at `http://localhost:3000`

## 🔧 Key Components

### Backend

- **server.py**: FastAPI application with REST endpoints for recommendations
- **rag_pipeline.py**: Implements the RAG pipeline for retrieval and generation
- **embeddings.py**: Generates semantic embeddings for documents
- **vector_store.py**: Manages ChromaDB vector database operations
- **scraper.py**: Handles web scraping for data collection
- **evaluation.py**: Tools for evaluating recommendation quality

### Frontend

- **HomePage.js**: Landing page and primary interface
- **EvaluationPage.js**: Assessment evaluation dashboard
- **UI Components**: Comprehensive Shadcn/UI component library for consistent design

## 📡 API Endpoints

### Health Check
```
GET /health
```

### Recommendations
```
POST /recommendations
Content-Type: application/json

{
  "query": "user query here"
}
```

### Search
```
POST /search
Content-Type: application/json

{
  "query": "search query"
}
```

## 🤖 Technology Stack

### Backend
- **Framework**: FastAPI
- **Vector DB**: ChromaDB
- **Embeddings**: Google Generative AI
- **LLM**: Google Gemini
- **Web Scraping**: BeautifulSoup4
- **Data Processing**: Pandas, NumPy

### Frontend
- **Framework**: React
- **UI Library**: Shadcn/UI (Tailwind CSS)
- **Build Tool**: Create React App with craco
- **State Management**: React Hooks
- **API Client**: Fetch API

## 📊 How It Works

1. **Data Collection**: The scraper collects relevant information from web sources
2. **Embedding Generation**: Documents are converted to semantic embeddings
3. **Vector Storage**: Embeddings are stored in ChromaDB for fast retrieval
4. **Query Processing**: User queries are embedded in the same vector space
5. **Retrieval**: Similar documents are retrieved from the vector store
6. **Generation**: Google Gemini generates contextual recommendations based on retrieved context
7. **Response**: Results are returned to the frontend for display

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 📈 Evaluation

The system includes evaluation metrics to assess recommendation quality. Use the Evaluation Page in the frontend to view performance metrics.

## 🔐 Security

- API keys are managed through environment variables
- CORS is configured appropriately for frontend-backend communication
- Input validation on all API endpoints

## 🐛 Troubleshooting

### Backend won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that the Google API key is set correctly
- Verify Python version is 3.9+

### Frontend won't load
- Clear node_modules and reinstall: `npm install`
- Clear cache: `npm cache clean --force`
- Check that backend API is running

### Vector store issues
- Ensure the `data/chroma/` directory exists and has write permissions
- Rebuild the vector store if corrupted

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on the repository.

---

**Last Updated**: December 2025

