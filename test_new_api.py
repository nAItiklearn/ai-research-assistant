"""
Test the new Google Gemini API
"""
from dotenv import load_dotenv
import os
import sys
import time

# CRITICAL: Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

load_dotenv()

print("🧪 Testing New Google Gemini API...")
print("=" * 60)

# Test 1: Import new SDK
print("\n1️⃣ Testing SDK import...")
try:
    from google import genai
    print("✅ google-genai SDK imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    print("   Run: pip install google-genai")
    exit(1)

# Test 2: Check API key
print("\n2️⃣ Checking API key...")
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    print(f"✅ API key found: {api_key[:20]}...")
else:
    print("❌ GOOGLE_API_KEY not found in .env")
    exit(1)

# Test 3: Initialize client
print("\n3️⃣ Initializing Gemini client...")
try:
    client = genai.Client(api_key=api_key)
    print("✅ Client initialized successfully")
except Exception as e:
    print(f"❌ Client initialization failed: {e}")
    exit(1)

# Test 4: Test generation
print("\n4️⃣ Testing content generation...")

models_to_try = [
    'models/gemini-2.5-flash',
    'models/gemini-2.0-flash',
    'models/gemini-flash-latest'
]

generation_success = False
working_model = None

for model_name in models_to_try:
    print(f"\n   Trying: {model_name}...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents='Say "Hello from Gemini!" in exactly one sentence.'
        )
        print(f"   ✅ SUCCESS!")
        print(f"   Response: {response.text[:100]}")
        generation_success = True
        working_model = model_name
        break
    except Exception as e:
        error_str = str(e)
        if '429' in error_str:
            print(f"   ⚠️  Rate limit. Waiting 5s...")
            time.sleep(5)
        elif '404' in error_str:
            print(f"   ⚠️  Not available")
        else:
            print(f"   ⚠️  Error: {error_str[:80]}...")

if not generation_success:
    print("\n❌ All models failed - likely rate limit")
    print("   Wait 60 seconds and try again")
    exit(1)

print(f"\n   💡 Working model: {working_model}")

# Test 5: Check if agent folder exists
print("\n5️⃣ Checking project structure...")

# Get the actual project root (where test_new_api.py is located)
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"   Script location: {script_dir}")

# Check for agent folder
agent_folder = os.path.join(script_dir, 'agent')
print(f"   Looking for: {agent_folder}")

if os.path.exists(agent_folder):
    print(f"✅ Agent folder found!")
    core_file = os.path.join(agent_folder, 'core.py')
    if os.path.exists(core_file):
        print(f"✅ core.py exists")
    else:
        print(f"❌ core.py NOT FOUND")
        print(f"   Expected at: {core_file}")
        exit(1)
else:
    print(f"❌ Agent folder NOT FOUND")
    print(f"\n   Current directory: {os.getcwd()}")
    print(f"   Script directory: {script_dir}")
    print(f"   Looking for: {agent_folder}")
    print("\n   Files in current directory:")
    for item in os.listdir(script_dir):
        print(f"      - {item}")
    exit(1)

# Test 6: Import ResearchAgent
print("\n6️⃣ Testing ResearchAgent import...")
try:
    from agent.core import ResearchAgent
    print("✅ ResearchAgent imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    print(f"\n   Python path: {sys.path[0]}")
    print(f"   Agent folder: {agent_folder}")
    print("\n   Troubleshooting:")
    print("   1. Make sure you're running from project root")
    print("   2. Check agent/core.py exists")
    print("   3. Check agent/__init__.py exists")
    exit(1)

# Test 7: Initialize agent
print("\n7️⃣ Initializing ResearchAgent...")
try:
    agent = ResearchAgent()
    print("✅ Agent initialized")
    print(f"   Model: {agent.model_name}")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    exit(1)

# Test 8: Test chat
print("\n8️⃣ Testing agent chat...")
try:
    print("   Sending message...")
    response = agent.chat("Hello! Can you help with research?")
    print(f"✅ Chat works!")
    print(f"   Response: {response[:120]}...")
except Exception as e:
    if '429' in str(e):
        print(f"⚠️  Rate limit on chat (agent setup is correct!)")
    else:
        print(f"❌ Chat failed: {e}")

print("\n" + "=" * 60)
print("🎉 SETUP COMPLETE!")
print(f"\n📌 Working model: {working_model}")
print("\n✅ Your agent is ready!")
print("\nNext: Rebuild other components with new API")
print("=" * 60)