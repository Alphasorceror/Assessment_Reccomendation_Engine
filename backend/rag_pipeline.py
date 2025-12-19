import os
from dotenv import load_dotenv
import logging
from typing import List, Dict
import asyncio
import re

import google.generativeai as genai
from google.generativeai.types import GenerateTextRequest

logger = logging.getLogger(__name__)
load_dotenv()

class RAGPipeline:
    def __init__(self, vector_store, embeddings_model):
        self.vector_store = vector_store
        self.embeddings = embeddings_model
        
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        # Configure the Gemini API client with your key
        genai.configure(api_key=self.api_key)

    async def recommend(self, query: str, n_results: int = 10) -> List[Dict]:
        try:
            logger.info(f"Processing query: {query}")
            
            # Step 1: Analyze the query
            query_analysis = await self._analyze_query(query)
            
            # Step 2: Generate embedding for query
            query_embedding = await self.embeddings.get_embedding(query)
            
            # Step 3: Retrieve candidates
            candidates = self.vector_store.search(query_embedding, n_results=20)
            
            if not candidates:
                return []
            
            # Step 4: Re-rank with LLM
            recommendations = await self._rerank_and_filter(
                query,
                query_analysis,
                candidates,
                n_results
            )
            
            # Balanced results
            balanced = self._balance_recommendations(recommendations, query_analysis)
            return balanced[:n_results]
            
        except Exception as e:
            logger.error(f"Error in recommendation pipeline: {str(e)}")
            return []

    async def _analyze_query(self, query: str) -> Dict:
        try:
            prompt = f"""Analyze this query and extract requirements.

Query: {query}

Return:
- Skills: […]
- Test Types: […]
- Experience: […]
- Focus: […]"""

            response = genai.models.generate_text(
                model="gemini-2.5-flash",
                input=prompt
            )
            text = response.text or ""
            
            return {
                'skills': self._extract_skills(text),
                'test_types': self._extract_test_types(text, query),
                'experience_level': self._extract_experience_level(text, query),
                'focus_areas': self._extract_focus_areas(text)
            }

        except Exception as e:
            logger.error(f"Error analyzing query: {str(e)}")
            return {
                'skills': [], 
                'test_types': ['Knowledge & Skills', 'Personality & Behavior'],
                'experience_level': 'Mid',
                'focus_areas': []
            }

    def _extract_skills(self, analysis: str) -> List[str]:
        skills = []
        lines = analysis.lower().split('\n')
        for line in lines:
            if 'skill' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    skills.extend([s.strip() for s in parts[1].split(',')])
        return skills
    
    def _extract_test_types(self, analysis: str, query: str) -> List[str]:
        text = f"{analysis} {query}".lower()
        types = []
        if any(k in text for k in ['technical', 'coding', 'programming']):
            types.append('Knowledge & Skills')
        if any(k in text for k in ['personality', 'leadership']):
            types.append('Personality & Behavior')
        if any(k in text for k in ['cognitive', 'analytical']):
            types.append('Cognitive')
        if not types:
            types = ['Knowledge & Skills']
        return types

    def _extract_experience_level(self, analysis: str, query: str) -> str:
        text = f"{analysis} {query}".lower()
        if 'senior' in text:
            return 'Senior'
        if 'junior' in text or 'entry' in text:
            return 'Entry'
        return 'Mid'

    def _extract_focus_areas(self, analysis: str) -> List[str]:
        focus = []
        for l in analysis.lower().split('\n'):
            if 'focus' in l:
                parts = l.split(':')
                if len(parts) > 1:
                    focus.extend([f.strip() for f in parts[1].split(',')])
        return focus

    async def _rerank_and_filter(self, query: str, analysis: Dict, candidates: List[Dict], n_results: int) -> List[Dict]:
        try:
            summary = "\n".join([f"{i+1}. {c['name']} - {c['description'][:100]}..."
                                 for i, c in enumerate(candidates[:15])])
            
            prompt = f"""Rank the top {n_results} relevant assessments.

Query: {query}

Candidates:
{summary}

Return only comma-separated ranking numbers."""
            
            response = genai.models.generate_text(
                model="gemini-2.5-flash",
                input=prompt
            )
            text = response.text or ""
            rankings = self._parse_rankings(text)
            
            reranked = []
            for r in rankings:
                if 0 <= r < len(candidates):
                    reranked.append(candidates[r])
            for i, c in enumerate(candidates):
                if i not in rankings and len(reranked) < n_results:
                    reranked.append(c)
            return reranked

        except Exception as e:
            logger.error(f"Error re-ranking: {str(e)}")
            return candidates

    def _parse_rankings(self, response: str) -> List[int]:
        nums = re.findall(r'\d+', response)
        return [int(n) - 1 for n in nums]

    def _balance_recommendations(self, recs: List[Dict], analysis: Dict) -> List[Dict]:
        req_types = analysis.get('test_types', [])
        if len(req_types) <= 1:
            return recs

        by_type = {}
        for r in recs:
            for t in r.get('test_type', []):
                by_type.setdefault(t, []).append(r)

        balanced = []
        seen = set()
        for t in req_types:
            if t in by_type:
                for r in by_type[t]:
                    if r.get('url') not in seen:
                        balanced.append(r)
                        seen.add(r.get('url'))
                        break
        for r in recs:
            if r.get('url') not in seen:
                balanced.append(r)
                seen.add(r.get('url'))
        return balanced
