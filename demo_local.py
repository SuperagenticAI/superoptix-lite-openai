"""
Live Demonstration: Code Reviewer Agent with LOCAL Models (Ollama)
Run this to use completely FREE local models!
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / 'openai_gepa'))

import asyncio
from openai_gepa.agents.code_reviewer.pipelines.code_reviewer_openai_pipeline import CodeReviewerPipeline

print("="*80)
print("🎯 Code Reviewer Agent - Local Demo (Ollama)")
print("="*80)
print()

# Initialize pipeline with local Ollama config
print("📦 Loading Code Reviewer Pipeline with LOCAL models...")
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

print("🔍 Running Code Reviews with LOCAL Ollama models...")
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
    print("🤖 Agent Review:")
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
    print("   Run 'python optimize_local.py' to generate optimized instructions!")

print()
print("="*80)
print("💡 This demo uses FREE local Ollama models!")
print("   No API costs, 100% private, runs on your machine.")
print("="*80)
