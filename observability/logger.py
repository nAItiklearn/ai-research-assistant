"""
Observability System - Logging, Tracing, and Metrics
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger
import sys

class ObservabilityManager:
    """
    Manages logging, tracing, and metrics for the multi-agent system
    """
    
    def __init__(self):
        # Setup logging
        self.setup_logging()
        
        # Metrics storage
        self.metrics = {
            'agent_calls': 0,
            'tool_executions': 0,
            'search_queries': 0,
            'papers_analyzed': 0,
            'api_calls': 0,
            'errors': 0
        }
        
        # Trace storage
        self.traces = []
        
        # Performance metrics
        self.performance = {
            'search_times': [],
            'analysis_times': [],
            'total_session_time': 0
        }
    
    def setup_logging(self):
        """Configure loguru logger"""
        # Remove default handler
        logger.remove()
        
        # Add console handler with custom format
        logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
            level="INFO"
        )
        
        # Add file handler
        os.makedirs('logs', exist_ok=True)
        logger.add(
            "logs/research_agent_{time}.log",
            rotation="1 day",
            retention="7 days",
            level="DEBUG"
        )
    
    def log_agent_call(self, agent_name: str, action: str, parameters: Dict = None):
        """Log agent activity"""
        self.metrics['agent_calls'] += 1
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'action': action,
            'parameters': parameters or {}
        }
        
        logger.info(f"Agent Call: {agent_name} - {action}")
        self.traces.append(log_entry)
    
    def log_tool_execution(self, tool_name: str, parameters: Dict, result: Any):
        """Log tool execution"""
        self.metrics['tool_executions'] += 1
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'tool': tool_name,
            'parameters': parameters,
            'success': bool(result)
        }
        
        logger.debug(f"Tool Executed: {tool_name}")
        self.traces.append(log_entry)
    
    def log_search(self, query: str, source: str, results_count: int):
        """Log search activity"""
        self.metrics['search_queries'] += 1
        
        logger.info(f"Search: {query} on {source} - {results_count} results")
    
    def log_analysis(self, papers_count: int, analysis_type: str):
        """Log analysis activity"""
        self.metrics['papers_analyzed'] += papers_count
        
        logger.info(f"Analysis: {analysis_type} on {papers_count} papers")
    
    def log_error(self, error: Exception, context: str):
        """Log error with context"""
        self.metrics['errors'] += 1
        
        logger.error(f"Error in {context}: {str(error)}")
        
        self.traces.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            'context': context,
            'error': str(error)
        })
    
    def record_performance(self, operation: str, duration: float):
        """Record performance metrics"""
        if operation == 'search':
            self.performance['search_times'].append(duration)
        elif operation == 'analysis':
            self.performance['analysis_times'].append(duration)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            **self.metrics,
            'avg_search_time': sum(self.performance['search_times']) / len(self.performance['search_times']) if self.performance['search_times'] else 0,
            'avg_analysis_time': sum(self.performance['analysis_times']) / len(self.performance['analysis_times']) if self.performance['analysis_times'] else 0,
            'total_traces': len(self.traces)
        }
    
    def get_traces(self, limit: int = 50) -> List[Dict]:
        """Get recent traces"""
        return self.traces[-limit:]
    
    def export_metrics(self, filepath: str):
        """Export metrics to file"""
        metrics_data = {
            'metrics': self.get_metrics(),
            'traces': self.traces,
            'performance': self.performance,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        logger.info(f"Metrics exported to {filepath}")
    
    def generate_report(self) -> str:
        """Generate observability report"""
        metrics = self.get_metrics()
        
        report = f"""
# Observability Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Metrics Summary
- Total Agent Calls: {metrics['agent_calls']}
- Tool Executions: {metrics['tool_executions']}
- Search Queries: {metrics['search_queries']}
- Papers Analyzed: {metrics['papers_analyzed']}
- API Calls: {metrics['api_calls']}
- Errors: {metrics['errors']}

## Performance
- Avg Search Time: {metrics['avg_search_time']:.2f}s
- Avg Analysis Time: {metrics['avg_analysis_time']:.2f}s
- Total Traces: {metrics['total_traces']}

## Recent Activity
"""
        
        recent_traces = self.get_traces(10)
        for trace in recent_traces:
            report += f"\n- [{trace.get('timestamp', 'N/A')}] "
            if 'agent' in trace:
                report += f"Agent: {trace['agent']} - {trace['action']}"
            elif 'tool' in trace:
                report += f"Tool: {trace['tool']}"
            elif 'type' in trace:
                report += f"Error: {trace.get('context', 'Unknown')}"
        
        return report

# Global instance
observability = ObservabilityManager()