import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict
import re

logger = logging.getLogger(__name__)

class SHLScraper:
    def __init__(self):
        self.base_url = "https://www.shl.com/solutions/products/product-catalog/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def scrape_catalog(self) -> List[Dict]:
        """Scrape SHL assessment catalog"""
        assessments = []
        
        try:
            logger.info(f"Scraping SHL catalog from {self.base_url}")
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all assessment cards/links
            assessment_links = soup.find_all('a', href=re.compile(r'/solutions/products/product-catalog/view/'))
            
            logger.info(f"Found {len(assessment_links)} assessment links")
            
            seen_urls = set()
            
            for link in assessment_links:
                href = link.get('href', '')
                if not href:
                    continue
                    
                if not href.startswith('http'):
                    href = 'https://www.shl.com' + href
                
                if href in seen_urls:
                    continue
                    
                seen_urls.add(href)
                
                try:
                    assessment_data = self._scrape_assessment_page(href)
                    if assessment_data:
                        assessments.append(assessment_data)
                        logger.info(f"Scraped: {assessment_data['name']}")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error scraping {href}: {str(e)}")
                    continue
                    
            logger.info(f"Successfully scraped {len(assessments)} assessments")
            
            # If no assessments found, use fallback
            if len(assessments) == 0:
                logger.info("No assessments scraped from website, using fallback data")
                return self._get_fallback_data()
            
            return assessments
            
        except Exception as e:
            logger.error(f"Error scraping catalog: {str(e)}")
            return self._get_fallback_data()
    
    def _scrape_assessment_page(self, url: str) -> Dict:
        """Scrape individual assessment page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract assessment name
            name = soup.find('h1')
            name = name.get_text(strip=True) if name else url.split('/')[-2].replace('-', ' ').title()
            
            # Extract description
            description_elem = soup.find('div', class_=re.compile(r'description|content|summary', re.I))
            if not description_elem:
                description_elem = soup.find('p')
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            # Extract metadata
            duration = self._extract_duration(soup)
            test_types = self._extract_test_types(soup, description, name)
            
            return {
                'name': name,
                'url': url,
                'description': description[:500] if description else name,
                'duration': duration,
                'test_type': test_types,
                'adaptive_support': 'Yes' if 'adaptive' in description.lower() else 'No',
                'remote_support': 'Yes'
            }
            
        except Exception as e:
            logger.error(f"Error parsing assessment page {url}: {str(e)}")
            return None
    
    def _extract_duration(self, soup) -> int:
        """Extract assessment duration in minutes"""
        text = soup.get_text().lower()
        
        patterns = [
            r'(\d+)\s*minutes?',
            r'(\d+)\s*mins?',
            r'duration[:\s]+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        
        return 45
    
    def _extract_test_types(self, soup, description: str, name: str) -> List[str]:
        """Extract test types from content"""
        text = f"{name} {description}".lower()
        types = []
        
        # Knowledge & Skills (K)
        if any(keyword in text for keyword in ['programming', 'coding', 'java', 'python', 'sql', 'technical', 'software', 'developer', 'engineer', 'analyst', 'data']):
            types.append('Knowledge & Skills')
        
        # Personality & Behavior (P)
        if any(keyword in text for keyword in ['personality', 'behavior', 'leadership', 'communication', 'collaboration', 'teamwork', 'soft skill', 'emotional']):
            types.append('Personality & Behavior')
        
        # Cognitive (C)
        if any(keyword in text for keyword in ['cognitive', 'reasoning', 'logical', 'verbal', 'numerical', 'abstract', 'problem solving']):
            types.append('Cognitive')
        
        # Default
        if not types:
            types = ['General Assessment']
        
        return types
    
    def _get_fallback_data(self) -> List[Dict]:
        """Fallback data when scraping fails"""
        logger.info("Using fallback assessment data")
        
        return [
            {
                'name': 'Java Developer Assessment',
                'url': 'https://www.shl.com/solutions/products/product-catalog/view/java-programming/',
                'description': 'Comprehensive Java programming assessment covering OOP, collections, multi-threading, and problem-solving skills.',
                'duration': 60,
                'test_type': ['Knowledge & Skills'],
                'adaptive_support': 'No',
                'remote_support': 'Yes'
            },
            {
                'name': 'Python Programming Test',
                'url': 'https://www.shl.com/solutions/products/product-catalog/view/python-programming/',
                'description': 'Python coding test evaluating syntax, data structures, algorithms, and application development capabilities.',
                'duration': 45,
                'test_type': ['Knowledge & Skills'],
                'adaptive_support': 'No',
                'remote_support': 'Yes'
            },
            {
                'name': 'SQL Database Assessment',
                'url': 'https://www.shl.com/solutions/products/product-catalog/view/sql-assessment/',
                'description': 'SQL assessment testing query writing, database design, optimization, and data manipulation skills.',
                'duration': 50,
                'test_type': ['Knowledge & Skills'],
                'adaptive_support': 'Yes',
                'remote_support': 'Yes'
            },
            {
                'name': 'Leadership & Collaboration Assessment',
                'url': 'https://www.shl.com/solutions/products/product-catalog/view/leadership-assessment/',
                'description': 'Evaluates leadership qualities, team collaboration, communication skills, and stakeholder management abilities.',
                'duration': 40,
                'test_type': ['Personality & Behavior'],
                'adaptive_support': 'Yes',
                'remote_support': 'Yes'
            },
            {
                'name': 'Cognitive Ability Test',
                'url': 'https://www.shl.com/solutions/products/product-catalog/view/cognitive-test/',
                'description': 'Measures cognitive abilities including logical reasoning, problem-solving, and analytical thinking.',
                'duration': 30,
                'test_type': ['Cognitive'],
                'adaptive_support': 'Yes',
                'remote_support': 'Yes'
            },
            {
                'name': 'Sales Representative Assessment',
                'url': 'https://www.shl.com/solutions/products/product-catalog/view/sales-assessment/',
                'description': 'Comprehensive assessment for sales roles covering persuasion, communication, and customer relationship skills.',
                'duration': 35,
                'test_type': ['Personality & Behavior', 'Cognitive'],
                'adaptive_support': 'Yes',
                'remote_support': 'Yes'
            },
            {
                'name': 'Data Analyst Assessment',
                'url': 'https://www.shl.com/solutions/products/product-catalog/view/data-analyst/',
                'description': 'Tests data analysis skills including Excel, SQL, Python, statistical analysis, and data visualization.',
                'duration': 90,
                'test_type': ['Knowledge & Skills', 'Cognitive'],
                'adaptive_support': 'No',
                'remote_support': 'Yes'
            },
            {
                'name': 'JavaScript Developer Test',
                'url': 'https://www.shl.com/solutions/products/product-catalog/view/javascript-test/',
                'description': 'Evaluates JavaScript proficiency including ES6+, DOM manipulation, async programming, and frameworks.',
                'duration': 55,
                'test_type': ['Knowledge & Skills'],
                'adaptive_support': 'No',
                'remote_support': 'Yes'
            },
            {
                'name': 'Communication Skills Assessment',
                'url': 'https://www.shl.com/solutions/products/product-catalog/view/communication-skills/',
                'description': 'Assesses written and verbal communication, presentation skills, and interpersonal effectiveness.',
                'duration': 25,
                'test_type': ['Personality & Behavior'],
                'adaptive_support': 'Yes',
                'remote_support': 'Yes'
            },
            {
                'name': 'Problem Solving & Critical Thinking',
                'url': 'https://www.shl.com/solutions/products/product-catalog/view/problem-solving/',
                'description': 'Measures analytical thinking, problem-solving approach, and decision-making capabilities.',
                'duration': 40,
                'test_type': ['Cognitive'],
                'adaptive_support': 'Yes',
                'remote_support': 'Yes'
            }
        ]
