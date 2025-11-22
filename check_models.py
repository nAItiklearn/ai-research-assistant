"""
Check which Gemini models are available
"""
from dotenv import load_dotenv
import os
import sys
from google import genai

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
client = genai.Client(api_key=api_key)

print("🔍 Checking available Gemini models...\n")

try:
    # List all available models
    models_response = client.models.list()
    
    print("✅ Available models:\n")
    
    # Convert to list if it's an iterator
    models_list = list(models_response)
    
    if models_list:
        for model in models_list:
            print(f"  ✓ {model.name}")
            try:
                print(f"    Display name: {model.display_name}")
            except:
                pass
            print()
    else:
        print("  No models returned. This is normal for free tier.\n")
    
except Exception as e:
    print(f"⚠️  Could not list models: {str(e)[:100]}\n")

print("=" * 60)
print("📋 RECOMMENDED MODELS TO USE (Free Tier - 2025):\n")
print("  1. models/gemini-2.5-flash  ← BEST CHOICE")
print("     - Latest Gemini 2.5")
print("     - Free tier")
print("     - Fast & capable\n")
print("  2. models/gemini-2.0-flash")
print("     - Stable Gemini 2.0")
print("     - Reliable\n")
print("  3. models/gemini-flash-latest")
print("     - Auto-updates to latest")
print("     - Always current")
print("=" * 60)

print("\n💡 Testing which one works for you...\n")

models_to_test = [
    'models/gemini-2.5-flash',
    'models/gemini-2.0-flash', 
    'models/gemini-flash-latest'
]

working_models = []

for model_name in models_to_test:
    try:
        response = client.models.generate_content(
            model=model_name,
            contents='Reply with just "OK"'
        )
        print(f"✅ {model_name} - WORKS!")
        working_models.append(model_name)
    except Exception as e:
        error_str = str(e)
        if '429' in error_str:
            print(f"⚠️  {model_name} - Rate limited (try again later)")
        elif '404' in error_str:
            print(f"❌ {model_name} - Not available")
        else:
            print(f"⚠️  {model_name} - Error: {error_str[:50]}...")

print("\n" + "=" * 60)
if working_models:
    print(f"✅ WORKING MODELS: {len(working_models)}\n")
    for m in working_models:
        print(f"   • {m}")
    print(f"\n💡 Use this in agent/core.py:")
    print(f"   self.model_name = '{working_models[0]}'")
else:
    print("⚠️  No models working right now.")
    print("   Possible reasons:")
    print("   1. Rate limit - wait 1 minute")
    print("   2. API key issue")
    print("   3. Network problem")
print("=" * 60)