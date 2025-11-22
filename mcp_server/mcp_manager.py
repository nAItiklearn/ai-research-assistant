"""
MCP (Model Context Protocol) Manager
Manages tool execution through MCP servers
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class MCPManager:
    """Manages Model Context Protocol tool integrations"""
    
    def __init__(self):
        self.tools = {}
        self.tool_history = []
        self.initialize_tools()
    
    def initialize_tools(self):
        """Initialize available MCP tools"""
        self.tools = {
            'search': {
                'name': 'search',
                'description': 'Search for academic papers and web content',
                'parameters': {
                    'query': 'string',
                    'source': 'arxiv|web|scholar',
                    'max_results': 'int'
                }
            },
            'analyze': {
                'name': 'analyze',
                'description': 'Analyze paper content and extract insights',
                'parameters': {
                    'paper_id': 'string',
                    'analysis_type': 'summary|evaluation|citation'
                }
            },
            'memory_store': {
                'name': 'memory_store',
                'description': 'Store information in long-term memory',
                'parameters': {
                    'key': 'string',
                    'value': 'any',
                    'context': 'string'
                }
            },
            'memory_retrieve': {
                'name': 'memory_retrieve',
                'description': 'Retrieve information from long-term memory',
                'parameters': {
                    'key': 'string',
                    'context': 'string'
                }
            },
            'file_write': {
                'name': 'file_write',
                'description': 'Write research findings to file',
                'parameters': {
                    'filename': 'string',
                    'content': 'string'
                }
            }
        }
    
    def get_available_tools(self) -> List[Dict]:
        """Get list of available tools for LLM"""
        return [
            {
                'name': tool['name'],
                'description': tool['description'],
                'parameters': tool['parameters']
            }
            for tool in self.tools.values()
        ]
    
    def execute_tool(self, tool_name: str, parameters: Dict) -> Dict[str, Any]:
        """Execute a tool through MCP protocol"""
        if tool_name not in self.tools:
            return {
                'success': False,
                'error': f'Tool {tool_name} not found'
            }
        
        # Log tool execution
        execution_log = {
            'tool': tool_name,
            'parameters': parameters,
            'timestamp': datetime.now().isoformat()
        }
        self.tool_history.append(execution_log)
        
        # Route to appropriate handler
        try:
            if tool_name == 'search':
                return self._handle_search(parameters)
            elif tool_name == 'analyze':
                return self._handle_analyze(parameters)
            elif tool_name == 'memory_store':
                return self._handle_memory_store(parameters)
            elif tool_name == 'memory_retrieve':
                return self._handle_memory_retrieve(parameters)
            elif tool_name == 'file_write':
                return self._handle_file_write(parameters)
            else:
                return {'success': False, 'error': 'Handler not implemented'}
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_search(self, params: Dict) -> Dict:
        """Handle search tool execution"""
        # This will be called by the search agent
        return {
            'success': True,
            'message': 'Search delegated to SearchAgent',
            'parameters': params
        }
    
    def _handle_analyze(self, params: Dict) -> Dict:
        """Handle analyze tool execution"""
        return {
            'success': True,
            'message': 'Analysis delegated to AnalysisAgent',
            'parameters': params
        }
    
    def _handle_memory_store(self, params: Dict) -> Dict:
        """Store information in memory"""
        key = params.get('key')
        value = params.get('value')
        context = params.get('context', '')
        
        # Create memory directory if not exists
        os.makedirs('data/memory', exist_ok=True)
        
        memory_file = 'data/memory/long_term_memory.json'
        
        # Load existing memory
        memory = {}
        if os.path.exists(memory_file):
            with open(memory_file, 'r') as f:
                memory = json.load(f)
        
        # Store new entry
        memory[key] = {
            'value': value,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save memory
        with open(memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
        
        return {
            'success': True,
            'message': f'Stored {key} in long-term memory'
        }
    
    def _handle_memory_retrieve(self, params: Dict) -> Dict:
        """Retrieve information from memory"""
        key = params.get('key')
        
        memory_file = 'data/memory/long_term_memory.json'
        
        if not os.path.exists(memory_file):
            return {
                'success': False,
                'error': 'No memory found'
            }
        
        with open(memory_file, 'r') as f:
            memory = json.load(f)
        
        if key in memory:
            return {
                'success': True,
                'data': memory[key]
            }
        else:
            return {
                'success': False,
                'error': f'Key {key} not found in memory'
            }
    
    def _handle_file_write(self, params: Dict) -> Dict:
        """Write content to file"""
        filename = params.get('filename')
        content = params.get('content')
        
        os.makedirs('data/outputs', exist_ok=True)
        filepath = f'data/outputs/{filename}'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'success': True,
            'message': f'Written to {filepath}'
        }
    
    def get_tool_history(self) -> List[Dict]:
        """Get history of tool executions"""
        return self.tool_history
    
    def clear_history(self):
        """Clear tool execution history"""
        self.tool_history = []