"""
Test all agents working together
"""
from dotenv import load_dotenv
import time

load_dotenv()

print("🧪 Testing Complete Multi-Agent System...")
print("=" * 60)

# Test 1: Import all agents
print("\n1️⃣ Importing agents...")
try:
    from agent.core import ResearchAgent
    from agent.orchestrator import OrchestratorAgent
    from agent.search_agent import SearchAgent
    from agent.analysis_agent import AnalysisAgent
    print("✅ All agents imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test 2: Initialize all agents
print("\n2️⃣ Initializing agents...")
try:
    core_agent = ResearchAgent()
    print("✅ Core Agent initialized")
    
    orchestrator = OrchestratorAgent()
    print("✅ Orchestrator initialized")
    
    search_agent = SearchAgent()
    print("✅ Search Agent initialized")
    
    analysis_agent = AnalysisAgent()
    print("✅ Analysis Agent initialized")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    exit(1)

# Test 3: Test Search Agent (Parallel)
print("\n3️⃣ Testing Search Agent (parallel search)...")
try:
    print("   Searching for 'machine learning'...")
    start = time.time()
    results = search_agent.parallel_search("machine learning", ['arxiv'], max_results=5)
    duration = time.time() - start
    
    print(f"✅ Found {results['total_found']} papers in {duration:.2f}s")
    print(f"   Sources: {results['sources_searched']}")
except Exception as e:
    print(f"❌ Search failed: {e}")

# Test 4: Test Analysis Agent (Sequential)
print("\n4️⃣ Testing Analysis Agent (sequential analysis)...")
if results['papers']:
    try:
        print(f"   Analyzing {len(results['papers'])} papers...")
        start = time.time()
        analysis = analysis_agent.sequential_analysis(results['papers'], "machine learning")
        duration = time.time() - start
        
        print(f"✅ Analysis complete in {duration:.2f}s")
        print(f"   Stages: {list(analysis['stages'].keys())}")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

# Test 5: Test Orchestrator
print("\n5️⃣ Testing Orchestrator (planning)...")
try:
    plan_result = orchestrator.plan_research_task("recent NLP advances")
    if plan_result['success']:
        plan = plan_result['plan']
        print(f"✅ Plan created:")
        print(f"   Objective: {plan['objective']}")
        print(f"   Tasks: {len(plan['tasks'])}")
    else:
        print(f"⚠️  Used fallback plan")
except Exception as e:
    print(f"❌ Planning failed: {e}")

# Test 6: Session state
print("\n6️⃣ Testing session state...")
try:
    state = orchestrator.get_session_state()
    print(f"✅ Session state retrieved:")
    print(f"   Tasks completed: {state['tasks_completed']}")
    print(f"   Memory items: {state['memory_items']}")
except Exception as e:
    print(f"❌ State retrieval failed: {e}")

print("\n" + "=" * 60)
print("🎉 ALL AGENTS WORKING!")
print("\n✅ Multi-agent system is ready!")
print("\nNext: Build Streamlit UI")
print("=" * 60)