import requests
import PyPDF2
import io
from typing import Optional, Dict
import re

class PDFProcessor:
    """Process and extract information from PDF papers"""
    
    def download_pdf(self, url: str) -> Optional[bytes]:
        """Download PDF from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            if 'application/pdf' in response.headers.get('Content-Type', ''):
                return response.content
            return None
        
        except Exception as e:
            print(f"PDF download error: {str(e)}")
            return None
    
    def extract_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages[:10]:  # First 10 pages only
                text += page.extract_text() + "\n"
            
            return text
        
        except Exception as e:
            print(f"PDF text extraction error: {str(e)}")
            return ""
    
    def extract_metadata(self, pdf_content: bytes) -> Dict:
        """Extract PDF metadata"""
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            metadata = {
                'num_pages': len(pdf_reader.pages),
                'title': '',
                'author': '',
                'subject': '',
                'creator': ''
            }
            
            if pdf_reader.metadata:
                metadata['title'] = pdf_reader.metadata.get('/Title', '')
                metadata['author'] = pdf_reader.metadata.get('/Author', '')
                metadata['subject'] = pdf_reader.metadata.get('/Subject', '')
                metadata['creator'] = pdf_reader.metadata.get('/Creator', '')
            
            return metadata
        
        except Exception as e:
            print(f"Metadata extraction error: {str(e)}")
            return {}
    
    def extract_abstract(self, text: str) -> str:
        """Extract abstract from paper text"""
        try:
            # Common abstract patterns
            patterns = [
                r'abstract[:\s]+(.*?)(?:introduction|keywords|\n\n)',
                r'abstract[:\s]+(.*?)(?:1\.|I\.)',
            ]
            
            text_lower = text.lower()
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
                if match:
                    abstract = match.group(1).strip()
                    # Clean up
                    abstract = re.sub(r'\s+', ' ', abstract)
                    return abstract[:1000]  # First 1000 chars
            
            # Fallback: return first paragraph after "abstract"
            if 'abstract' in text_lower:
                idx = text_lower.index('abstract')
                remaining = text[idx:idx+1500]
                return remaining.split('\n\n')[1] if '\n\n' in remaining else remaining[:500]
            
            return ""
        
        except Exception as e:
            print(f"Abstract extraction error: {str(e)}")
            return ""
    
    def extract_citations(self, text: str) -> list:
        """Extract citation count or references"""
        try:
            # Look for references section
            references_patterns = [
                r'references\s+(.*?)(?:appendix|\Z)',
                r'bibliography\s+(.*?)(?:appendix|\Z)',
            ]
            
            text_lower = text.lower()
            for pattern in references_patterns:
                match = re.search(pattern, text_lower, re.DOTALL)
                if match:
                    refs_text = match.group(1)
                    # Count number of reference entries (rough estimate)
                    ref_count = len(re.findall(r'\[\d+\]|\n\d+\.', refs_text))
                    return ref_count
            
            return 0
        
        except:
            return 0
    
    def process_paper_url(self, url: str) -> Dict:
        """Download and process a paper from URL"""
        result = {
            'success': False,
            'text': '',
            'abstract': '',
            'metadata': {},
            'num_references': 0
        }
        
        pdf_content = self.download_pdf(url)
        if not pdf_content:
            return result
        
        result['text'] = self.extract_text(pdf_content)
        result['abstract'] = self.extract_abstract(result['text'])
        result['metadata'] = self.extract_metadata(pdf_content)
        result['num_references'] = self.extract_citations(result['text'])
        result['success'] = True
        
        return result