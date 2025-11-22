"""
Core Research Agent - Updated for google-genai SDK
"""
import os
import json
from typing import List, Dict, Any
from datetime import datetime
from google import genai
from google.genai import types

class ResearchAgent:
    """Main Research Assistant Agent using Google Gemini"""
    
    def __init__(self):
        # Initialize Gemini with NEW API
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        # Create client with new SDK
        self.client = genai.Client(api_key=api_key)
        # Use Gemini 2.5 Flash - Latest stable free tier model
        self.model_name = 'models/gemini-2.5-flash'
        
        # Initialize conversation history
        self.conversation_history = []
        self.research_context = {
            'papers_found': [],
            'queries_made': [],
            'user_preferences': {}
        }
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_context_summary(self) -> str:
        """Create a summary of research context"""
        summary_parts = []
        
        if self.research_context['queries_made']:
            recent_queries = self.research_context['queries_made'][-3:]
            summary_parts.append(f"Previous queries: {', '.join(recent_queries)}")
        
        if self.research_context['papers_found']:
            summary_parts.append(f"Found {len(self.research_context['papers_found'])} papers so far")
        
        return " | ".join(summary_parts) if summary_parts else "New research session"
    
    def plan_research_steps(self, query: str) -> List[str]:
        """Plan multi-step research approach"""
        planning_prompt = f"""You are a research planning assistant. Break down this research query into 2-4 specific search steps.

Query: {query}
Context: {self.get_context_summary()}

Return ONLY a JSON array of search steps. Example:
["machine learning healthcare applications", "recent ML healthcare papers 2024", "healthcare ML evaluation metrics"]

JSON array:"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=planning_prompt
            )
            
            steps_text = response.text.strip()
            
            # Clean JSON extraction
            if '```json' in steps_text:
                steps_text = steps_text.split('```json')[1].split('```')[0].strip()
            elif '```' in steps_text:
                steps_text = steps_text.split('```')[1].split('```')[0].strip()
            
            # Remove any markdown or extra text
            if '[' in steps_text and ']' in steps_text:
                start = steps_text.index('[')
                end = steps_text.rindex(']') + 1
                steps_text = steps_text[start:end]
            
            steps = json.loads(steps_text)
            return steps if isinstance(steps, list) else [query]
        except Exception as e:
            print(f"Planning error: {e}")
            return [query]
    
    def evaluate_paper_relevance(self, paper: Dict, query: str) -> float:
        """Score paper relevance (0-1)"""
        score = 0.0
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        # Title matching
        title = paper.get('title', '').lower()
        title_terms = set(title.split())
        if query_terms and title_terms:
            overlap = len(query_terms & title_terms)
            score += (overlap / len(query_terms)) * 0.4
        
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
        
        return min(score, 1.0)
    
    def synthesize_findings(self, papers: List[Dict], query: str) -> str:
        """Generate comprehensive research summary"""
        if not papers:
            return "No papers found for this query."
        
        # Prepare paper summaries (top 5 only)
        papers_text = []
        for i, paper in enumerate(papers[:5], 1):
            title = paper.get('title', 'Unknown')
            authors = ', '.join(paper.get('authors', ['Unknown'])[:3])
            year = paper.get('year', 'Unknown')
            summary = paper.get('summary', paper.get('snippet', ''))[:300]
            
            papers_text.append(
                f"{i}. {title} ({year})\n"
                f"   Authors: {authors}\n"
                f"   {summary}..."
            )
        
        papers_context = '\n\n'.join(papers_text)
        
        synthesis_prompt = f"""Analyze these research papers and provide structured insights.

Research Query: {query}

Papers:
{papers_context}

Provide a concise analysis with:
1. Main Themes: Key themes across papers
2. Key Findings: Important discoveries
3. Research Gaps: Areas needing more research
4. Recommendations: Most relevant papers and why

Keep it clear and insightful (300-400 words)."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=synthesis_prompt
            )
            return response.text
        except Exception as e:
            return f"Synthesis generation failed: {str(e)}"
    
    def chat(self, user_message: str) -> str:
        """Main chat interface"""
        self.add_message('user', user_message)
        
        # Build context
        recent_history = self.conversation_history[-6:]
        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in recent_history[:-1]
        ])
        
        system_prompt = f"""You are an intelligent research assistant agent.

Conversation History:
{history_text}

Research Context: {self.get_context_summary()}

User: {user_message}

Respond helpfully. If they're asking for research help, indicate you'll search for papers."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=system_prompt
            )
            assistant_message = response.text
            self.add_message('assistant', assistant_message)
            return assistant_message
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.add_message('assistant', error_msg)
            return error_msg
    
    def save_session(self, filepath: str):
        """Save research session"""
        session_data = {
            'conversation_history': self.conversation_history,
            'research_context': self.research_context,
            'timestamp': datetime.now().isoformat()
        }
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    def load_session(self, filepath: str):
        """Load research session"""
        try:
            with open(filepath, 'r') as f:
                session_data = json.load(f)
            self.conversation_history = session_data.get('conversation_history', [])
            self.research_context = session_data.get('research_context', {})
            return True
        except Exception as e:
            print(f"Load error: {e}")
            return False