"""
Simple Working Streamlit UI for Multi-Agent Research Assistant
"""
import streamlit as st
import sys
import os
from datetime import datetime
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
# Load environment variables
# In production (Streamlit Cloud), use st.secrets
# Locally, use .env file
try:
    # Try Streamlit secrets first (for deployed app)
    if hasattr(st, 'secrets'):
        os.environ['GOOGLE_API_KEY'] = st.secrets.get("GOOGLE_API_KEY", "")
        os.environ['SERPER_API_KEY'] = st.secrets.get("SERPER_API_KEY", "")
except:
    # Fall back to .env file (for local development)
    load_dotenv()
from agent.orchestrator import OrchestratorAgent
from agent.search_agent import SearchAgent
from agent.analysis_agent import AnalysisAgent
from observability.logger import observability

# Page config
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .paper-card {
        background: white;
        color: #000;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .paper-card h4 {
        color: #1a237e !important;
        margin: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = OrchestratorAgent()
    st.session_state.search_agent = SearchAgent()
    st.session_state.analysis_agent = AnalysisAgent()
    st.session_state.research_results = None

# Header
st.markdown('<div class="main-header">🔬 AI Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Multi-Agent System | Powered by Google Gemini 2.5</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎛️ System Dashboard")
    
    # Metrics
    metrics = observability.get_metrics()
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{metrics['agent_calls']}</h3>
            <p>Agent Calls</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{metrics['search_queries']}</h3>
            <p>Searches</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Session info
    session_state = st.session_state.orchestrator.get_session_state()
    st.markdown("### 📊 Session Info")
    st.info(f"""
    **Tasks:** {session_state['tasks_completed']}  
    **Memory:** {session_state['memory_items']}  
    **Agents:** {len(session_state['active_agents'])}
    """)
    
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.orchestrator.reset_session()
        st.session_state.research_results = None
        st.rerun()

# Main content
st.markdown("## 🔬 Start Your Research")

# Research query input
col1, col2 = st.columns([3, 1])

with col1:
    research_query = st.text_input(
        "Enter your research question:",
        placeholder="e.g., What are recent advances in transformer models?",
        key="research_query"
    )

with col2:
    max_papers = st.number_input("Max papers:", min_value=5, max_value=20, value=10)

# Search button
if st.button("🚀 Start Research", type="primary", use_container_width=True):
    if not research_query:
        st.warning("Please enter a research question!")
    else:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Planning
        status_text.text("🧠 Orchestrator planning research...")
        progress_bar.progress(20)
        
        observability.log_agent_call("Orchestrator", "plan_research_task", {"query": research_query})
        plan_result = st.session_state.orchestrator.plan_research_task(research_query)
        
        if plan_result['success']:
            plan = plan_result['plan']
            st.success(f"✅ Plan: {plan['objective']}")
        else:
            plan = plan_result['fallback_plan']
            st.info("Using fallback plan")
        
        # Step 2: Search
        status_text.text("🔍 Search Agent executing parallel search...")
        progress_bar.progress(40)
        
        observability.log_agent_call("SearchAgent", "parallel_search", {"query": research_query})
        
        start_time = time.time()
        search_results = st.session_state.search_agent.parallel_search(
            research_query,
            sources=['arxiv', 'web'],
            max_results=max_papers
        )
        search_duration = time.time() - start_time
        
        observability.log_search(research_query, "arxiv+web", search_results['total_found'])
        observability.record_performance('search', search_duration)
        
        st.success(f"✅ Found {search_results['total_found']} papers in {search_duration:.2f}s")
        progress_bar.progress(60)
        
        # Step 3: Analysis
        if search_results['papers']:
            status_text.text("📊 Analysis Agent processing results...")
            progress_bar.progress(80)
            
            observability.log_agent_call("AnalysisAgent", "sequential_analysis", {"papers": len(search_results['papers'])})
            
            start_time = time.time()
            analysis_results = st.session_state.analysis_agent.sequential_analysis(
                search_results['papers'],
                research_query
            )
            analysis_duration = time.time() - start_time
            
            observability.log_analysis(len(search_results['papers']), 'sequential_pipeline')
            observability.record_performance('analysis', analysis_duration)
            
            st.success(f"✅ Analysis complete in {analysis_duration:.2f}s")
            progress_bar.progress(100)
            
            # Store results
            st.session_state.research_results = {
                'query': research_query,
                'search': search_results,
                'analysis': analysis_results,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in memory
            st.session_state.orchestrator.store_in_memory(
                f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                st.session_state.research_results,
                importance='high'
            )
            
            status_text.text("✅ Research complete!")
        
        else:
            st.warning("No papers found. Try different keywords.")
            progress_bar.progress(100)

# Display results
if st.session_state.research_results:
    st.markdown("---")
    st.markdown("## 📋 Research Results")
    
    results = st.session_state.research_results
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📄 Papers", "🔬 Analysis", "📊 Metrics"])
    
    # Tab 1: Papers
    with tab1:
        st.markdown(f"### Found {results['search']['total_found']} Papers")
        
        for i, paper in enumerate(results['search']['papers'][:15], 1):
            # Get URL
            paper_url = paper.get('pdf_url') or paper.get('link') or paper.get('url') or '#'
            
            with st.expander(f"📄 {i}. {paper.get('title', 'Untitled')}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Authors:** {', '.join(paper.get('authors', ['Unknown'])[:3])}")
                    st.markdown(f"**Year:** {paper.get('year', 'N/A')} | **Source:** {paper.get('search_source', 'Unknown')}")
                    
                    summary = paper.get('summary') or paper.get('snippet', 'No summary available.')
                    st.markdown(f"**Summary:** {summary[:300]}...")
                
                with col2:
                    if paper_url != '#':
                        st.link_button("📥 View Paper", paper_url)
    
    # Tab 2: Analysis
    with tab2:
        if 'analysis' in results:
            analysis = results['analysis']
            
            # Synthesis
            if 'synthesis' in analysis['stages']:
                st.markdown("### 📊 Research Synthesis")
                st.markdown(analysis['stages']['synthesis'])
            
            st.markdown("---")
            
            # Key Findings
            if 'findings' in analysis['stages']:
                st.markdown("### 🔑 Key Findings")
                for finding in analysis['stages']['findings']:
                    st.info(f"**{finding['paper']}**\n\n{finding['finding']}")
            
            st.markdown("---")
            
            # Research Gaps
            if 'gaps' in analysis['stages']:
                st.markdown("### 🎯 Research Gaps")
                for gap in analysis['stages']['gaps']:
                    st.warning(gap)
    
    # Tab 3: Metrics
    with tab3:
        st.markdown("### 📊 System Metrics")
        
        metrics = observability.get_metrics()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Agent Calls", metrics['agent_calls'])
            st.metric("Searches", metrics['search_queries'])
        
        with col2:
            st.metric("Tool Executions", metrics['tool_executions'])
            st.metric("Papers Analyzed", metrics['papers_analyzed'])
        
        with col3:
            st.metric("Avg Search Time", f"{metrics['avg_search_time']:.2f}s")
            st.metric("Avg Analysis Time", f"{metrics['avg_analysis_time']:.2f}s")
        
        st.markdown("---")
        
        # Recent traces
        st.markdown("### 📜 Recent Activity")
        traces = observability.get_traces(10)
        
        for trace in reversed(traces[-5:]):
            if 'agent' in trace:
                st.text(f"🤖 {trace['agent']} - {trace['action']}")
            elif 'tool' in trace:
                st.text(f"🔧 Tool: {trace['tool']}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🤖 Multi-Agent Research Assistant | Built with Streamlit & Google Gemini</p>
    <p><strong>Kaggle Agents Intensive Capstone 2025</strong></p>
</div>
""", unsafe_allow_html=True)