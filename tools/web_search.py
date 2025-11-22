import os
import requests
from typing import List, Dict
import re

class WebSearchTool:
    """Search the web using Serper API"""
    
    def __init__(self):
        self.api_key = os.getenv('SERPER_API_KEY')
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found in environment")
        self.base_url = "https://google.serper.dev/search"
    
    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search web for papers and articles"""
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': num_results
            }
            
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Process organic results
            for item in data.get('organic', []):
                result = {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'web'
                }
                
                # Try to extract year from title or snippet
                year_match = re.search(r'\b(20\d{2})\b', item.get('title', '') + ' ' + item.get('snippet', ''))
                if year_match:
                    result['year'] = int(year_match.group(1))
                
                results.append(result)
            
            return results
        
        except Exception as e:
            print(f"Web search error: {str(e)}")
            return []
    
    def search_scholar(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search Google Scholar specifically"""
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Add scholar-specific terms to query
            scholar_query = f"{query} site:scholar.google.com OR filetype:pdf research paper"
            
            payload = {
                'q': scholar_query,
                'num': num_results
            }
            
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('organic', []):
                # Filter for academic sources
                if any(domain in item.get('link', '') for domain in 
                       ['scholar.google', 'arxiv', 'acm.org', 'ieee.org', 'springer', 'sciencedirect']):
                    result = {
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'scholar'
                    }
                    
                    # Extract year
                    year_match = re.search(r'\b(20\d{2})\b', item.get('title', '') + ' ' + item.get('snippet', ''))
                    if year_match:
                        result['year'] = int(year_match.group(1))
                    
                    results.append(result)
            
            return results
        
        except Exception as e:
            print(f"Scholar search error: {str(e)}")
            return []
    
    def search_recent_papers(self, query: str, year: int = 2024) -> List[Dict]:
        """Search for recent papers from specific year"""
        recent_query = f"{query} {year} research paper"
        return self.search(recent_query, num_results=10)