"""
Search Agent - Specialized agent for parallel paper searches
"""
import sys
import os
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.arxiv_search import ArxivSearchTool
from tools.web_search import WebSearchTool

class SearchAgent:
    """
    Specialized agent for searching academic papers across multiple sources
    Executes parallel searches for efficiency
    """
    
    def __init__(self):
        self.arxiv_tool = ArxivSearchTool()
        self.web_tool = WebSearchTool()
        self.search_history = []
    
    def parallel_search(self, query: str, sources: List[str] = None, max_results: int = 10) -> Dict[str, Any]:
        """
        Execute parallel searches across multiple sources
        
        Args:
            query: Search query
            sources: List of sources ['arxiv', 'web', 'scholar']
            max_results: Maximum results per source
        
        Returns:
            Aggregated results from all sources
        """
        if sources is None:
            sources = ['arxiv', 'web']
        
        results = {
            'query': query,
            'sources_searched': [],
            'papers': [],
            'total_found': 0,
            'errors': []
        }
        
        # Use ThreadPoolExecutor for parallel searches
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            # Submit all search tasks
            future_to_source = {}
            
            for source in sources:
                if source == 'arxiv':
                    future = executor.submit(self._search_arxiv, query, max_results)
                    future_to_source[future] = 'arxiv'
                
                elif source == 'web':
                    future = executor.submit(self._search_web, query, max_results)
                    future_to_source[future] = 'web'
                
                elif source == 'scholar':
                    future = executor.submit(self._search_scholar, query, max_results)
                    future_to_source[future] = 'scholar'
            
            # Collect results as they complete
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    papers = future.result()
                    results['papers'].extend(papers)
                    results['sources_searched'].append(source)
                    results['total_found'] += len(papers)
                except Exception as e:
                    results['errors'].append({
                        'source': source,
                        'error': str(e)
                    })
        
        # Log search
        self.search_history.append({
            'query': query,
            'sources': sources,
            'results_count': results['total_found']
        })
        
        return results
    
    def _search_arxiv(self, query: str, max_results: int) -> List[Dict]:
        """Search arXiv"""
        try:
            papers = self.arxiv_tool.search(query, max_results)
            # Add source tag
            for paper in papers:
                paper['search_source'] = 'arxiv'
            return papers
        except Exception as e:
            print(f"ArXiv search error: {e}")
            return []
    
    def _search_web(self, query: str, max_results: int) -> List[Dict]:
        """Search web"""
        try:
            results = self.web_tool.search(query, max_results)
            # Add source tag
            for result in results:
                result['search_source'] = 'web'
            return results
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    def _search_scholar(self, query: str, max_results: int) -> List[Dict]:
        """Search Google Scholar"""
        try:
            results = self.web_tool.search_scholar(query, max_results)
            # Add source tag
            for result in results:
                result['search_source'] = 'scholar'
            return results
        except Exception as e:
            print(f"Scholar search error: {e}")
            return []
    
    def search_by_criteria(self, criteria: Dict) -> Dict[str, Any]:
        """
        Advanced search with multiple criteria
        
        Args:
            criteria: {
                'keywords': ['machine learning', 'healthcare'],
                'year_min': 2020,
                'year_max': 2024,
                'sources': ['arxiv', 'web'],
                'max_results': 10
            }
        """
        keywords = criteria.get('keywords', [])
        year_min = criteria.get('year_min')
        year_max = criteria.get('year_max')
        sources = criteria.get('sources', ['arxiv', 'web'])
        max_results = criteria.get('max_results', 10)
        
        # Build query
        query = ' '.join(keywords)
        
        # Execute parallel search
        results = self.parallel_search(query, sources, max_results)
        
        # Filter by year if specified
        if year_min or year_max:
            filtered_papers = []
            for paper in results['papers']:
                year = paper.get('year', 0)
                if year_min and year < year_min:
                    continue
                if year_max and year > year_max:
                    continue
                filtered_papers.append(paper)
            
            results['papers'] = filtered_papers
            results['total_found'] = len(filtered_papers)
        
        return results
    
    def search_related_papers(self, paper_title: str, max_results: int = 5) -> List[Dict]:
        """
        Find papers related to a given paper
        Uses the title to search for similar work
        """
        query = paper_title
        results = self.parallel_search(query, ['arxiv', 'web'], max_results)
        return results['papers']
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get statistics about searches performed"""
        total_searches = len(self.search_history)
        total_results = sum(s['results_count'] for s in self.search_history)
        
        return {
            'total_searches': total_searches,
            'total_results': total_results,
            'average_results': total_results / total_searches if total_searches > 0 else 0,
            'recent_queries': [s['query'] for s in self.search_history[-5:]]
        }