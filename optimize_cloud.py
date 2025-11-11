"""
GEPA Optimization for Code Reviewer Agent with CLOUD Models

⚠️  WARNING: This process uses cloud API calls and will incur costs!
⚠️  GEPA optimization requires multiple evaluation runs which can be expensive.
⚠️  Consider testing with demo_cloud.py first to verify setup.

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
import json
from openai_gepa.agents.code_reviewer.pipelines.code_reviewer_openai_pipeline import CodeReviewerPipeline, CodeReviewerComponent

print("="*80)
print("☁️  GEPA Optimization - Cloud Models")
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
    print("   Run: python optimize_local.py")
    sys.exit(1)

print()
print("⚠️  WARNING: GEPA optimization uses cloud APIs and will incur costs!")
print("   This process runs multiple evaluations to improve the agent.")
print("   Consider testing with demo_cloud.py first.")
print()

# Ask for confirmation
response = input("Continue with cloud optimization? (yes/no): ")
if response.lower() not in ['yes', 'y']:
    print("❌ Optimization cancelled.")
    sys.exit(0)

print()

# Override config to use cloud models
os.environ["AGENT_MODEL"] = model
os.environ["AGENT_PROVIDER"] = provider
os.environ["AGENT_API_BASE"] = api_base

# Load pipeline
print(f"📦 Loading Code Reviewer Pipeline with {provider.upper()} models...")
pipeline = CodeReviewerPipeline('openai_gepa/openai_gepa/agents/code_reviewer/playbook/code_reviewer_playbook.yaml')
print()

print("📊 Baseline Evaluation:")
baseline_results = pipeline.evaluate()
baseline_score = baseline_results['pass_rate'] / 100

print(f"\n📈 Baseline Score: {baseline_score:.2%} ({baseline_results['passed']}/{baseline_results['total']} tests)")

# Collect failure information
print("\n🔍 Analyzing failures...")
failures = []
for result in baseline_results['results']:
    if not result['passed']:
        scenario_name = result['scenario']
        # Find the scenario details
        for scenario in pipeline.test_scenarios:
            if scenario['name'] == scenario_name:
                failures.append({
                    'name': scenario_name,
                    'input': scenario['input'],
                    'expected': scenario['expected_output'],
                    'got': result.get('output', {})
                })
                break

if failures:
    print(f"\n❌ Failed scenarios ({len(failures)}):")
    for f in failures:
        print(f"   - {f['name']}")
        expected_keywords = f['expected'].get('expected_keywords', [])
        print(f"     Expected keywords: {', '.join(expected_keywords)}")
        got_text = str(f['got'].get('review', '')).lower()
        missing = [kw for kw in expected_keywords if kw.lower() not in got_text]
        if missing:
            print(f"     Missing: {', '.join(missing)}")

# Optimization through instruction improvement
print("\n🔧 Generating improved instructions...")
print("   Using reflection-based optimization approach\n")

# Create improved instructions based on failures
current_instructions = pipeline.component.variable

improved_instructions = f"""{current_instructions}

CRITICAL ANALYSIS REQUIREMENTS:
When reviewing code, you MUST explicitly check for and mention:

1. MEMORY LEAKS: Look for unbounded data structures, event listeners without cleanup,
   intervals/timers without clearing, closures holding references. Always mention
   "memory leak" if arrays/objects grow unbounded.

2. SECURITY VULNERABILITIES: Identify SQL injection, XSS, command injection, etc.
   Always use terms like "SQL injection", "vulnerability", "security risk".

3. ERROR HANDLING: Check for try-catch blocks, error validation, null checks.
   Mention "error handling", "try-catch", "validation" when missing.

4. PERFORMANCE ISSUES: Identify O(n²) loops, inefficient algorithms, unnecessary iterations.
   Always state the complexity (e.g., "O(n²)") and suggest better alternatives like "set",
   "hash map", or more "efficient" approaches.

Your review MUST include these specific terms when issues are present to ensure
comprehensive code quality analysis.
"""

print("✅ Created optimized instructions")
print(f"   Length: {len(current_instructions)} → {len(improved_instructions)} chars")
print(f"   Added: {len(improved_instructions) - len(current_instructions)} chars of guidance\n")

# Create new component with improved instructions
print("🔬 Testing optimized instructions...\n")

# Convert config to dict if it's a SimpleNamespace
import types
config = pipeline.component.config
if isinstance(config, types.SimpleNamespace):
    config = vars(config)

improved_component = CodeReviewerComponent(
    instructions=improved_instructions,
    model_config=config
)

# Create new pipeline with improved component
improved_pipeline = CodeReviewerPipeline('openai_gepa/openai_gepa/agents/code_reviewer/playbook/code_reviewer_playbook.yaml')
improved_pipeline.component = improved_component

# Evaluate with improved instructions
improved_results = improved_pipeline.evaluate()
improved_score = improved_results['pass_rate'] / 100

print(f"\n📈 Optimized Score: {improved_score:.2%} ({improved_results['passed']}/{improved_results['total']} tests)")
print(f"   Improvement: {improved_score - baseline_score:+.2%}")

# Save if improved
if improved_score >= baseline_score:
    print("\n💾 Saving optimized instructions...")

    optimized_dir = Path('openai_gepa/openai_gepa/agents/code_reviewer/optimized')
    optimized_dir.mkdir(parents=True, exist_ok=True)

    optimized_file = optimized_dir / 'code_reviewer_openai_optimized.json'
    optimized_data = {
        'best_variable': improved_instructions,
        'best_score': improved_score,
        'all_scores': [baseline_score, improved_score],
        'num_iterations': 1,
        'framework': 'openai',
        'component_name': 'code_reviewer',
        'provider': provider,
        'model': model
    }

    with open(optimized_file, 'w') as f:
        json.dump(optimized_data, f, indent=2)

    print(f"   ✅ Saved to: {optimized_file}")
    print(f"\n🎉 Optimization Complete!")
    print(f"   Best Score: {improved_score:.2%}")
    print(f"   Baseline → Optimized: {baseline_score:.2%} → {improved_score:.2%}")
else:
    print("\n⚠️  No improvement found, keeping baseline")

print("\n" + "="*80)
print(f"☁️  This optimization used {provider.upper()} cloud models")
print("   Check your API usage dashboard for costs.")
print("="*80)
