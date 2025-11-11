"""
Live Demonstration: Code Reviewer Agent with CLOUD Models
Prerequisites:
- Set your API key: export OPENAI_API_KEY=sk-...
- Or use Anthropic: export ANTHROPIC_API_KEY=sk-ant-...
- Or use Google: export GOOGLE_API_KEY=...
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / 'openai_gepa'))

import asyncio
from openai_gepa.agents.code_reviewer.pipelines.code_reviewer_openai_pipeline import CodeReviewerPipeline

print("="*80)
print("☁️  Code Reviewer Agent - Cloud Demo")
print("="*80)
print()

# Detect which cloud provider to use based on API keys
provider = None
model = None
api_base = None

if os.getenv("OPENAI_API_KEY"):
    provider = "openai"
    model = "gpt-5"  # Latest OpenAI model
    api_base = "https://api.openai.com/v1"
    print("✅ Using OpenAI (gpt-5)")
elif os.getenv("ANTHROPIC_API_KEY"):
    provider = "anthropic"
    model = "claude-sonnet-4.5"  # Latest Claude model
    api_base = "https://api.anthropic.com/v1"
    print("✅ Using Anthropic (claude-sonnet-4.5)")
elif os.getenv("GOOGLE_API_KEY"):
    provider = "google"
    model = "gemini-pro-2.5"  # Latest Gemini model
    api_base = "https://generativelanguage.googleapis.com/v1"
    print("✅ Using Google (gemini-pro-2.5)")
else:
    print("❌ Error: No API key found!")
    print()
    print("Please set one of the following:")
    print("  export OPENAI_API_KEY=sk-...")
    print("  export ANTHROPIC_API_KEY=sk-ant-...")
    print("  export GOOGLE_API_KEY=...")
    print()
    print("💡 Want to use FREE local models instead?")
    print("   Run: python demo_local.py")
    sys.exit(1)

print()

# Override config to use cloud models
os.environ["AGENT_MODEL"] = model
os.environ["AGENT_PROVIDER"] = provider
os.environ["AGENT_API_BASE"] = api_base

# Initialize pipeline
print(f"📦 Loading Code Reviewer Pipeline with {provider.upper()} models...")
pipeline = CodeReviewerPipeline(
    'openai_gepa/openai_gepa/agents/code_reviewer/playbook/code_reviewer_playbook.yaml'
)
print()

# Test samples
test_cases = [
    {
        "name": "SQL Injection Vulnerability",
        "code": """def get_user(username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return db.execute(query)""",
        "language": "python"
    },
    {
        "name": "Memory Leak",
        "code": """function processData() {
  let data = [];
  setInterval(() => {
    data.push(fetchData());
  }, 1000);
}""",
        "language": "javascript"
    },
    {
        "name": "Missing Error Handling",
        "code": """async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  const data = await response.json();
  return data;
}""",
        "language": "javascript"
    },
    {
        "name": "Inefficient Algorithm (O(n²))",
        "code": """def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i+1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates""",
        "language": "python"
    }
]

print(f"🔍 Running Code Reviews with {provider.upper()} cloud models...")
print("="*80)
print()

for i, test in enumerate(test_cases, 1):
    print(f"\n{'─'*80}")
    print(f"📝 Test Case {i}/{len(test_cases)}: {test['name']}")
    print(f"{'─'*80}")
    print()
    print(f"Code ({test['language']}):")
    print("```")
    print(test['code'])
    print("```")
    print()
    print(f"🤖 Agent Review (using {model}):")
    print("─" * 80)

    # Run review
    result = asyncio.run(pipeline.run(
        code=test['code'],
        language=test['language']
    ))

    review = result['review']
    print(review)
    print()

print("="*80)
print("✅ All reviews completed!")
print("="*80)
print()

# Show optimization status
if pipeline.is_trained:
    print("🎉 Agent is using GEPA-optimized instructions!")
    print("   The reviews above used automatically-loaded optimized prompts.")
else:
    print("ℹ️  Agent is using baseline instructions (no optimization file found).")
    print(f"   Run 'python optimize_cloud.py' to optimize with {provider.upper()}!")

print()
print("="*80)
print(f"☁️  This demo used {provider.upper()} cloud models")
print("   Check your API usage dashboard for costs.")
print("="*80)
