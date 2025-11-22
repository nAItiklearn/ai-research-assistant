import arxiv
from typing import List, Dict
import re

class ArxivSearchTool:
    """Search academic papers on arXiv"""
    
    def __init__(self):
        self.client = arxiv.Client()
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search arXiv for papers"""
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            papers = []
            for result in self.client.results(search):
                paper = {
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'summary': result.summary,
                    'published': result.published.strftime('%Y-%m-%d'),
                    'year': result.published.year,
                    'pdf_url': result.pdf_url,
                    'arxiv_id': result.entry_id.split('/')[-1],
                    'categories': result.categories,
                    'source': 'arXiv'
                }
                papers.append(paper)
            
            return papers
        
        except Exception as e:
            print(f"ArXiv search error: {str(e)}")
            return []
    
    def get_paper_by_id(self, arxiv_id: str) -> Dict:
        """Get specific paper by arXiv ID"""
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            result = next(self.client.results(search))
            
            return {
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'summary': result.summary,
                'published': result.published.strftime('%Y-%m-%d'),
                'year': result.published.year,
                'pdf_url': result.pdf_url,
                'arxiv_id': result.entry_id.split('/')[-1],
                'categories': result.categories,
                'source': 'arXiv'
            }
        except Exception as e:
            print(f"Error fetching paper {arxiv_id}: {str(e)}")
            return None
    
    def search_by_category(self, category: str, max_results: int = 10) -> List[Dict]:
        """Search papers by arXiv category (e.g., 'cs.AI', 'cs.LG')"""
        try:
            search = arxiv.Search(
                query=f"cat:{category}",
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            papers = []
            for result in self.client.results(search):
                paper = {
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'summary': result.summary,
                    'published': result.published.strftime('%Y-%m-%d'),
                    'year': result.published.year,
                    'pdf_url': result.pdf_url,
                    'arxiv_id': result.entry_id.split('/')[-1],
                    'categories': result.categories,
                    'source': 'arXiv'
                }
                papers.append(paper)
            
            return papers
        
        except Exception as e:
            print(f"Category search error: {str(e)}")
            return []