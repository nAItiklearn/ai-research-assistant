"""
Orchestrator Agent - Main coordinator for multi-agent system
Updated for google-genai SDK
"""
import os
import json
from typing import List, Dict, Any, Optional
from google import genai
from datetime import datetime
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp_server.mcp_manager import MCPManager

"""
Orchestrator Agent - Central Coordinator for Multi-Agent System

This demonstrates KEY HACKATHON REQUIREMENTS:
1. Multi-agent coordination - Plans and dispatches tasks to specialized agents
2. MCP integration - Uses Model Context Protocol for standardized tool execution
3. Sessions & Memory - Manages state with long-term memory bank storage
4. Context Engineering - Implements context compaction to prevent token overflow

Design Decision: Orchestrator pattern chosen for:
- Clear separation of concerns (each agent has specific role)
- Scalable architecture (easy to add new agents)
- Observable execution (every action is logged and traceable)
- Fault tolerance (agents operate independently)

Author: nAItiklearn | Kaggle Agents Intensive Capstone 2024
"""
class OrchestratorAgent:
    """Main orchestrator that coordinates multiple specialized agents"""
    
    def __init__(self):
        # Initialize Gemini with NEW API
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'models/gemini-2.5-flash'
        
        # Initialize MCP Manager
        self.mcp_manager = MCPManager()
        
        # State management
        self.session_state = {
            'current_task': None,
            'task_history': [],
            'agents_active': [],
            'context': {}
        }
        
        # Memory bank (long-term storage)
        self.memory_bank = {}
        self.load_memory_bank()
    
    def load_memory_bank(self):
        """Load long-term memory"""
        memory_file = 'data/memory/long_term_memory.json'
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r') as f:
                    self.memory_bank = json.load(f)
            except:
                self.memory_bank = {}
    
    def save_memory_bank(self):
        """Save long-term memory"""
        os.makedirs('data/memory', exist_ok=True)
        memory_file = 'data/memory/long_term_memory.json'
        with open(memory_file, 'w') as f:
            json.dump(self.memory_bank, f, indent=2)
    
    def plan_research_task(self, user_query: str) -> Dict[str, Any]:
        """Analyze user query and create a multi-step research plan"""
        
        planning_prompt = f"""You are a research orchestrator. Analyze this query and create an execution plan.

User Query: {user_query}

Context: {json.dumps(self.session_state.get('context', {}), indent=2)}

Create a JSON plan:
{{
  "objective": "clear research goal",
  "tasks": [
    {{
      "id": 1,
      "description": "task description",
      "agent": "SearchAgent",
      "tools": ["search"],
      "parameters": {{}},
      "priority": "high"
    }}
  ],
  "execution_mode": "sequential"
}}

Return ONLY valid JSON:"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=planning_prompt
            )
            plan_text = response.text.strip()
            
            # Extract JSON
            if '```json' in plan_text:
                plan_text = plan_text.split('```json')[1].split('```')[0].strip()
            elif '```' in plan_text:
                plan_text = plan_text.split('```')[1].split('```')[0].strip()
            
            # Find JSON object
            if '{' in plan_text and '}' in plan_text:
                start = plan_text.index('{')
                end = plan_text.rindex('}') + 1
                plan_text = plan_text[start:end]
            
            plan = json.loads(plan_text)
            
            # Store task
            self.session_state['current_task'] = plan
            self.session_state['task_history'].append({
                'query': user_query,
                'plan': plan,
                'timestamp': datetime.now().isoformat()
            })
            
            return {'success': True, 'plan': plan}
        
        except Exception as e:
            print(f"Planning error: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_plan': self._create_fallback_plan(user_query)
            }
    
    def _create_fallback_plan(self, query: str) -> Dict:
        """Create a simple fallback plan"""
        return {
            'objective': query,
            'tasks': [
                {
                    'id': 1,
                    'description': f'Search for papers on: {query}',
                    'agent': 'SearchAgent',
                    'tools': ['search'],
                    'parameters': {'query': query, 'max_results': 10},
                    'priority': 'high'
                },
                {
                    'id': 2,
                    'description': 'Analyze found papers',
                    'agent': 'AnalysisAgent',
                    'tools': ['analyze'],
                    'parameters': {},
                    'priority': 'medium'
                }
            ],
            'execution_mode': 'sequential'
        }
    
    def execute_plan(self, plan: Dict) -> Dict[str, Any]:
        """Execute the research plan"""
        results = {
            'objective': plan.get('objective', ''),
            'tasks_completed': [],
            'outputs': {},
            'errors': []
        }
        
        tasks = plan.get('tasks', [])
        execution_mode = plan.get('execution_mode', 'sequential')
        
        if execution_mode == 'sequential':
            for task in tasks:
                task_result = self._execute_task(task)
                results['tasks_completed'].append(task['id'])
                results['outputs'][task['id']] = task_result
                self.session_state['context'][f"task_{task['id']}"] = task_result
        
        return results
    
    def _execute_task(self, task: Dict) -> Dict[str, Any]:
        """Execute a single task"""
        agent = task.get('agent')
        tools = task.get('tools', [])
        parameters = task.get('parameters', {})
        
        # Log agent activation
        self.session_state['agents_active'].append(agent)
        
        # Execute tools through MCP
        tool_results = []
        for tool in tools:
            result = self.mcp_manager.execute_tool(tool, parameters)
            tool_results.append(result)
        
        return {
            'agent': agent,
            'tools_used': tools,
            'results': tool_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def compress_context(self, max_tokens: int = 2000) -> str:
        """Context compaction - summarize long context"""
        context = self.session_state.get('context', {})
        
        if not context:
            return ""
        
        summary_prompt = f"""Summarize this research context concisely (under {max_tokens} tokens):

{json.dumps(context, indent=2)}

Focus on: key findings, important papers, research direction.
Return a brief summary."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=summary_prompt
            )
            return response.text
        except:
            # Fallback: just take first N chars
            context_str = json.dumps(context)
            return context_str[:max_tokens * 4]
    
    def store_in_memory(self, key: str, value: Any, importance: str = 'medium'):
        """Store information in long-term memory bank"""
        self.memory_bank[key] = {
            'value': value,
            'importance': importance,
            'timestamp': datetime.now().isoformat()
        }
        self.save_memory_bank()
        
        # Also use MCP memory tool
        self.mcp_manager.execute_tool('memory_store', {
            'key': key,
            'value': value,
            'context': importance
        })
    
    def retrieve_from_memory(self, key: str) -> Optional[Any]:
        """Retrieve from long-term memory"""
        if key in self.memory_bank:
            return self.memory_bank[key]['value']
        
        # Try MCP retrieval
        result = self.mcp_manager.execute_tool('memory_retrieve', {'key': key})
        if result.get('success'):
            return result.get('data', {}).get('value')
        
        return None
    
    def get_session_state(self) -> Dict:
        """Get current session state"""
        return {
            'current_task': self.session_state['current_task'],
            'active_agents': list(set(self.session_state['agents_active'])),
            'tasks_completed': len(self.session_state['task_history']),
            'memory_items': len(self.memory_bank),
            'tool_executions': len(self.mcp_manager.get_tool_history())
        }
    
    def reset_session(self):
        """Reset current session (keep memory bank)"""
        self.session_state = {
            'current_task': None,
            'task_history': [],
            'agents_active': [],
            'context': {}
        }
        self.mcp_manager.clear_history()