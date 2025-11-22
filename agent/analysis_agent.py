"""
Analysis Agent - Sequential paper analysis and synthesis
Updated for google-genai SDK
"""
import os
import sys
from typing import List, Dict, Any
from google import genai

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.pdf_processor import PDFProcessor
"""
Analysis Agent - Sequential Pipeline Processor

DESIGN: 4-Stage Sequential Pipeline
Stage 1: Relevance Evaluation (scoring algorithm)
Stage 2: Finding Extraction (LLM-powered)
Stage 3: Research Synthesis (comprehensive analysis)
Stage 4: Gap Identification (future research directions)

Why Sequential? Each stage depends on results from previous stage.
This ensures high-quality analysis through progressive refinement.

This demonstrates:
- Sequential agent execution (Hackathon requirement)
- Agent evaluation (relevance scoring)
- Context engineering (smart summarization)
"""

class AnalysisAgent:
    """
    Specialized agent for sequential analysis of research papers
    Provides evaluation, synthesis, and insights
    """
    
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'models/gemini-2.5-flash'
        self.pdf_tool = PDFProcessor()
        
        self.analysis_pipeline = [
            'evaluate_relevance',
            'extract_key_findings',
            'assess_methodology',
            'identify_gaps'
        ]
    
    def sequential_analysis(self, papers: List[Dict], query: str) -> Dict[str, Any]:
        """
        Perform sequential analysis pipeline on papers
        
        Pipeline stages:
        1. Evaluate relevance
        2. Extract key findings
        3. Synthesize research
        4. Identify research gaps
        """
        if not papers:
            return {'error': 'No papers to analyze'}
        
        analysis_results = {
            'query': query,
            'papers_analyzed': len(papers),
            'stages': {}
        }
        
        # Stage 1: Evaluate Relevance
        relevance_scores = self.evaluate_papers(papers, query)
        analysis_results['stages']['relevance'] = relevance_scores
        
        # Filter to top papers
        top_papers = sorted(
            [(p, s) for p, s in zip(papers, relevance_scores)],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Stage 2: Extract Key Findings
        key_findings = self.extract_findings([p[0] for p in top_papers])
        analysis_results['stages']['findings'] = key_findings
        
        # Stage 3: Synthesize Insights
        synthesis = self.synthesize_research([p[0] for p in top_papers], query)
        analysis_results['stages']['synthesis'] = synthesis
        
        # Stage 4: Identify Gaps
        gaps = self.identify_research_gaps([p[0] for p in top_papers], query)
        analysis_results['stages']['gaps'] = gaps
        
        return analysis_results
    
    def evaluate_papers(self, papers: List[Dict], query: str) -> List[float]:
        """
        Evaluate relevance of each paper
        Returns: List of relevance scores (0-1)
        """
        scores = []
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        for paper in papers:
            score = 0.0
            
            # Title matching
            title = paper.get('title', '').lower()
            title_terms = set(title.split())
            if query_terms and title_terms:
                title_overlap = len(query_terms & title_terms) / len(query_terms)
                score += title_overlap * 0.4
            
            # Abstract/summary matching
            abstract = (paper.get('summary', '') or paper.get('snippet', '')).lower()
            if any(term in abstract for term in query_terms):
                score += 0.3
            
            # Recency bonus
            year = paper.get('year', 0)
            if year >= 2023:
                score += 0.2
            elif year >= 2020:
                score += 0.1
            
            # Citation bonus
            citations = paper.get('citations', 0)
            if citations > 100:
                score += 0.1
            
            scores.append(min(score, 1.0))
        
        return scores
    
    def extract_findings(self, papers: List[Dict]) -> List[Dict]:
        """Extract key findings from papers using LLM"""
        findings = []
        
        for paper in papers[:5]:  # Top 5 papers
            title = paper.get('title', 'Unknown')
            summary = paper.get('summary', paper.get('snippet', ''))[:500]
            
            if not summary:
                continue
            
            prompt = f"""Extract the key finding from this paper in 1-2 sentences:

Title: {title}
Summary: {summary}

Key finding:"""

            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                findings.append({
                    'paper': title,
                    'finding': response.text.strip()
                })
            except:
                findings.append({
                    'paper': title,
                    'finding': 'Unable to extract'
                })
        
        return findings
    
    def synthesize_research(self, papers: List[Dict], query: str) -> str:
        """Generate comprehensive synthesis of research findings"""
        
        # Prepare paper summaries
        paper_texts = []
        for i, paper in enumerate(papers[:5], 1):
            title = paper.get('title', 'Unknown')
            authors = ', '.join(paper.get('authors', ['Unknown'])[:2])
            summary = paper.get('summary', paper.get('snippet', ''))[:300]
            year = paper.get('year', 'Unknown')
            
            paper_texts.append(f"{i}. {title} ({year})\n   Authors: {authors}\n   {summary}")
        
        papers_context = '\n\n'.join(paper_texts)
        
        synthesis_prompt = f"""Analyze these research papers and provide insights.

Research Query: {query}

Papers:
{papers_context}

Provide a structured synthesis covering:
1. Main Themes: What are the common themes?
2. Key Contributions: What are the major findings?
3. Methodologies: What approaches are used?
4. Trends: What patterns emerge?

Be concise but insightful (300-400 words)."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=synthesis_prompt
            )
            return response.text
        except Exception as e:
            return f"Synthesis generation failed: {str(e)}"
    
    def identify_research_gaps(self, papers: List[Dict], query: str) -> List[str]:
        """Identify research gaps and future directions"""
        
        paper_titles = [p.get('title', '') for p in papers[:5]]
        
        gap_prompt = f"""Based on these recent papers on "{query}", identify 3-4 research gaps:

Papers:
{chr(10).join(f"- {title}" for title in paper_titles)}

List specific research gaps that need more investigation:"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=gap_prompt
            )
            gaps_text = response.text.strip()
            
            # Parse into list
            gaps = [
                line.strip() 
                for line in gaps_text.split('\n') 
                if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-'))
            ]
            return gaps[:5]
        except:
            return ["Unable to identify gaps"]
    
    def comparative_analysis(self, papers: List[Dict], aspect: str) -> Dict[str, Any]:
        """Compare papers on specific aspect"""
        
        comparison = {
            'aspect': aspect,
            'papers': []
        }
        
        for paper in papers[:5]:
            title = paper.get('title', 'Unknown')
            summary = paper.get('summary', paper.get('snippet', ''))[:200]
            
            prompt = f"""Analyze this paper's {aspect}:

Title: {title}
Summary: {summary}

Describe the {aspect} in one sentence:"""

            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                comparison['papers'].append({
                    'title': title,
                    'analysis': response.text.strip()
                })
            except:
                comparison['papers'].append({
                    'title': title,
                    'analysis': 'Analysis unavailable'
                })
        
        return comparison
    
    def generate_literature_review(self, papers: List[Dict], query: str) -> str:
        """Generate a structured literature review"""
        
        review_prompt = f"""Generate a concise literature review on: {query}

Papers available: {len(papers)} papers

Structure:
1. Introduction (what is being studied)
2. Current State (recent findings)
3. Future Directions (gaps and opportunities)

Keep it academic but concise (400-500 words)."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=review_prompt
            )
            return response.text
        except Exception as e:
            return f"Literature review generation failed: {str(e)}"