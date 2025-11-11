# OpenAI Agents SDK + GEPA Optimization Demo

> **Build self-optimizing AI agents with OpenAI SDK and automated prompt engineering**

This is a complete working example showing how to build AI agents using the official OpenAI Agents SDK and optimize them automatically with GEPA (Genetic Evaluation-based Prompt Augmentation) from SuperOptiX.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-green.svg)](https://github.com/openai/agents-sdk)

---

## ✨ What's Included

- **Complete Code Reviewer Agent** - Production-ready agent that detects security issues, memory leaks, and performance problems
- **GEPA Optimization Demo** - Automated prompt engineering example (custom implementation)
- **BDD Test Scenarios** - Measurable evaluation with behavior-driven tests
- **100% Local** - Works with Ollama (no API keys needed!)
- **Auto-Loading** - Optimized prompts load automatically after training
- **Standalone** - Includes minimal SuperOptiX components (no external dependencies)

> **Note**: This demo includes `superoptix_lite` - minimal components needed for GEPA-style optimization. For production use with full SuperOptiX features, install: `pip install superoptix[frameworks-openai]`

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install Ollama from https://ollama.ai

# Pull models - choose any models you prefer!
# Example options:
ollama pull gpt-oss:20b       # Fast, good quality (recommended for task)
ollama pull gpt-oss:120b      # Slower, best quality (for reflection or task)
ollama pull llama3.1:8b       # Fastest (for quick experiments)

# Recommended configurations:
# - Balanced: gpt-oss:20b (task) + gpt-oss:20b (reflection)
# - Quality: gpt-oss:20b (task) + gpt-oss:120b (reflection)
# - Speed: gpt-oss:20b (task) + llama3.1:8b (reflection)
```

**System Requirements:**
- Python 3.11+
- 16GB+ RAM (32GB+ recommended for gpt-oss:120b)
- Ollama running locally

### 2. Install

```bash
# Clone repository
git clone <your-repo-url>
cd openai_superoptix

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Try the Demo (Baseline)

```bash
# Try the code reviewer with baseline instructions
python demo_optimized_agent.py
```

This will demonstrate the agent reviewing 4 code samples with baseline instructions:
- ✅ SQL injection vulnerabilities
- ✅ Memory leaks
- ✅ Missing error handling
- ✅ Performance issues (O(n²) algorithms)

**Note:** First run uses baseline instructions. Run the optimization (step 4) to improve performance!

### 4. Run GEPA Optimization (Optional)

```bash
# Optimize the agent's instructions using GEPA
python optimize_code_reviewer.py
```

This will:
1. ✅ Evaluate baseline performance (runs all BDD test scenarios)
2. ✅ Analyze failures and identify missing keywords
3. ✅ Generate improved instructions
4. ✅ Test the improved version
5. ✅ Save optimized weights (if improved)

After optimization completes, run `python demo_optimized_agent.py` again to see the agent using optimized instructions!

---

## 📖 Usage Examples

### Basic Code Review

```python
import asyncio
from openai_gepa.agents.code_reviewer.pipelines.code_reviewer_openai_pipeline import CodeReviewerPipeline

# Initialize agent
pipeline = CodeReviewerPipeline(
    'openai_gepa/openai_gepa/agents/code_reviewer/playbook/code_reviewer_playbook.yaml'
)

# Review some code
code = """
def get_user(username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return db.execute(query)
"""

result = asyncio.run(pipeline.run(code=code, language="python"))
print(result["review"])
```

**Output:**
```
⚠️  Critical Security Issue: SQL Injection Vulnerability

This code is vulnerable to SQL injection. The username parameter is directly
concatenated into the SQL query without sanitization...

Recommendations:
1. Use parameterized queries: cursor.execute("SELECT * FROM users WHERE name = ?", (username,))
2. Consider using an ORM (SQLAlchemy, Django ORM)
3. Validate and sanitize all user input
...
```

## 🏗️ Project Structure

```
openai_superoptix/
├── README.md                                  # This file
├── LICENSE                                    # MIT License
├── requirements.txt                           # Python dependencies
│
├── optimize_code_reviewer.py                 # Run GEPA optimization
├── demo_optimized_agent.py                    # Live agent demo
│
└── openai_gepa/                               # Main project
    ├── pyproject.toml                         # Package configuration
    └── openai_gepa/                           # Python package
        └── agents/
            ├── code_reviewer/                 # ⭐ Code reviewer agent
            │   ├── playbook/
            │   │   └── code_reviewer_playbook.yaml       # Config + BDD tests
            │   ├── pipelines/
            │   │   └── code_reviewer_openai_pipeline.py  # Agent code
            │   └── optimized/
            │       └── code_reviewer_openai_optimized.json  # GEPA results
            │
            └── assistant_openai/              # Simple Q&A assistant
                ├── playbook/
                ├── pipelines/
                └── optimized/
```

---

## 🔍 How It Works

### 1. Native OpenAI SDK Agent

Written using official OpenAI Agents SDK patterns:

```python
from agents import Agent, Runner, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

class CodeReviewerAgent:
    def __init__(self, instructions, model, api_base):
        # Initialize Ollama-compatible model
        self.model = OpenAIChatCompletionsModel(
            model=model,
            openai_client=AsyncOpenAI(
                base_url=f"{api_base}/v1",
                api_key="ollama"  # Dummy key for Ollama
            )
        )

        # Create agent
        self.agent = Agent(
            name="Code Reviewer",
            instructions=instructions,  # ← GEPA optimizes this!
            model=self.model
        )

    async def review_code(self, code, language):
        result = await Runner.run(self.agent, input=code)
        return result.final_message.content
```

### 2. SuperOptiX Integration

Wrapped in `BaseComponent` for GEPA compatibility:

```python
# Using minimal BaseComponent from included superoptix_lite package
from openai_gepa.superoptix_lite import BaseComponent

class CodeReviewerComponent(BaseComponent):
    def __init__(self, instructions=None, model_config=None):
        super().__init__(
            name="code_reviewer",
            variable=instructions,      # ← GEPA optimizes this variable
            variable_type="instructions",
            framework="openai"
        )
```

> **Note**: This demo includes `superoptix_lite` - a minimal implementation of SuperOptiX's BaseComponent. For production use with full GEPA capabilities, install the complete SuperOptiX framework.

### 3. BDD Test Scenarios

Performance measured with test scenarios in the playbook:

```yaml
feature_specifications:
  scenarios:
    - name: SQL Injection Detection
      input:
        code: |
          def get_user(username):
              query = "SELECT * FROM users WHERE name = '" + username + "'"
              return db.execute(query)
        language: python
      expected_output:
        expected_keywords:
          - SQL injection
          - vulnerability
          - parameterized
```

### 4. GEPA Optimization Process

1. **Baseline**: Evaluates agent with original instructions
2. **Analysis**: Identifies which test scenarios fail and why
3. **Improvement**: Generates enhanced instructions with explicit requirements
4. **Testing**: Validates improved version against all scenarios
5. **Saving**: Stores optimized instructions for automatic loading

### 5. Automatic Loading

On next initialization, optimized instructions load transparently:

```python
# Check for optimization file (happens automatically in __init__)
optimized_file = playbook_dir / "optimized" / "code_reviewer_openai_optimized.json"

if optimized_file.exists():
    opt_data = json.load(open(optimized_file))
    optimized_instructions = opt_data['best_variable']
    print(f"✅ Loaded optimized instructions (score: {score:.2%})")
    self.is_trained = True
```

---

## ⚙️ Customizing Models

You can easily customize which models to use for the agent and GEPA optimization:

### 1. Change Agent Model

Edit the playbook YAML file:

```yaml
# openai_gepa/openai_gepa/agents/code_reviewer/playbook/code_reviewer_playbook.yaml
spec:
  language_model:
    provider: ollama
    model: ollama:gpt-oss:120b    # ← Change this to any Ollama model
    api_base: http://localhost:11434
```

### 2. Change GEPA Reflection Model

Edit the same playbook YAML file:

```yaml
# openai_gepa/openai_gepa/agents/code_reviewer/playbook/code_reviewer_playbook.yaml
optimization:
  optimizer:
    reflection_lm: ollama:gpt-oss:120b    # ← Change reflection model here
```

**Model Selection Tips:**

- **Same models**: Use the same model for both (e.g., gpt-oss:20b) for consistency
- **Stronger reflection**: Use a larger model for reflection (e.g., gpt-oss:120b) for better optimization quality
- **Faster optimization**: Use a smaller model for reflection (e.g., llama3.1:8b) for speed
- **Any Ollama model**: Works with any model available in Ollama

**Example Configurations:**

```yaml
# Quality-focused (slower, better results)
model: ollama:gpt-oss:20b
reflection_lm: ollama:gpt-oss:120b

# Balanced (good speed and quality)
model: ollama:gpt-oss:20b
reflection_lm: ollama:gpt-oss:20b

# Speed-focused (faster, good enough)
model: ollama:gpt-oss:20b
reflection_lm: ollama:llama3.1:8b
```

---

## 🎯 Creating Your Own Agent

### Step 1: Define Playbook with BDD Tests

```yaml
# my_agent_playbook.yaml
apiVersion: agent/v1
kind: AgentSpec
metadata:
  name: my_agent
spec:
  target_framework: openai
  language_model:
    provider: ollama
    model: ollama:gpt-oss:20b
    api_base: http://localhost:11434

  feature_specifications:
    scenarios:
      - name: Test Case 1
        input:
          text: "Sample input"
        expected_output:
          expected_keywords:
            - keyword1
            - keyword2
```

### Step 2: Implement OpenAI SDK Agent

```python
from agents import Agent, Runner, OpenAIChatCompletionsModel

class MyAgent:
    def __init__(self, instructions, model, api_base):
        self.model = OpenAIChatCompletionsModel(...)
        self.agent = Agent(
            name="My Agent",
            instructions=instructions,
            model=self.model
        )

    async def execute(self, text):
        result = await Runner.run(self.agent, input=text)
        return result.final_message.content
```

### Step 3: Add SuperOptiX Wrapper

```python
# Using minimal BaseComponent from superoptix_lite (included in this demo)
from openai_gepa.superoptix_lite import BaseComponent

class MyComponent(BaseComponent):
    def __init__(self, instructions=None):
        super().__init__(
            variable=instructions or "Default instructions",
            variable_type="instructions",
            framework="openai"
        )
```

### Step 4: Create Pipeline with Evaluation

```python
class MyPipeline:
    def __init__(self, playbook_path):
        self.component = MyComponent(
            instructions=self._load_optimization()  # Auto-load if exists
        )
        self.test_scenarios = self._load_bdd_scenarios()

    def evaluate(self):
        # Run all test scenarios and measure pass rate
        pass
```

---

## 🐛 Troubleshooting

### Ollama Connection Issues

```bash
# Verify Ollama is running
ollama list

# Test a model
ollama run gpt-oss:20b "Hello"

# Check API endpoint
curl http://localhost:11434/api/tags
```

### Module Import Errors

```bash
# Ensure you're in the right directory and venv is activated
cd openai_superoptix
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify openai-agents is installed
pip show openai-agents
```

### OPENAI_API_KEY Warnings

These warnings are **safe to ignore** when using Ollama:
```
OPENAI_API_KEY is not set, skipping trace export
[non-fatal] Tracing client error 401
```

The agent works perfectly with local Ollama models without any API keys.

---

## 📊 Performance Results

### Code Reviewer Agent

| Metric | Value |
|--------|-------|
| **Test Pass Rate** | 4/4 scenarios (100%) |
| **Scenarios Tested** | SQL injection, memory leaks, error handling, performance |
| **Detection Accuracy** | Identifies all critical issues |
| **Model** | Ollama gpt-oss:20b |

**GEPA Optimization:**
- Original instructions: ~900 characters
- Optimized instructions: ~1,900 characters (+106%)
- Adds explicit detection requirements for common issues
- Ensures consistent use of technical terminology

---

## 📚 About SuperOptiX Lite

This demo includes `superoptix_lite` - a minimal, standalone implementation of the key SuperOptiX components needed for agent optimization:

### What's Included
- **BaseComponent** - Base class for creating optimizable agents
- **Variable management** - Interface for GEPA-style optimization
- **Framework integration** - Compatible with OpenAI Agents SDK

### What's NOT Included (Full SuperOptiX Only)
- ❌ Full GEPA optimizer (UniversalGEPA)
- ❌ Multi-framework compilation (DSPy, CrewAI, Google ADK, Microsoft, DeepAgents)
- ❌ Advanced RAG optimization
- ❌ MCP protocol optimization
- ❌ Memory system optimization
- ❌ Orchestra (multi-agent coordination)
- ❌ CLI tools (`super` command)
- ❌ Observability integrations (MLFlow, LangFuse, W&B)

### Production Use

For production deployments with full optimization capabilities:

```bash
pip install superoptix[frameworks-openai]
```

Then use the full framework:
```python
from superoptix.core.base_component import BaseComponent
from superoptix.optimizers.universal_gepa import UniversalGEPA
```

See the [SuperOptiX documentation](https://docs.super-agentic.ai) for complete features.

---

## 📚 Learn More

### Documentation

- **[OpenAI Agents SDK](https://github.com/openai/agents-sdk)** - Official SDK documentation
- **[SuperOptiX](https://docs.super-agentic.ai)** - Full GEPA optimization framework
- **[Ollama](https://ollama.ai)** - Local LLM inference

### Tutorials

For a complete step-by-step tutorial on building agents with OpenAI SDK and optimizing with GEPA, see the [SuperOptiX documentation](https://docs.super-agentic.ai/tutorials/openai-sdk-gepa-optimization).

---

## 🤝 Contributing

Contributions welcome! Feel free to:

- Report bugs via GitHub Issues
- Suggest new agent examples
- Submit pull requests for improvements
- Share your own agents built with this template

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI Agents SDK** - Excellent agent framework
- **SuperOptiX** - GEPA optimization capabilities
- **Ollama** - Making local LLM inference accessible

---

<div align="center">

**Made with ❤️ using OpenAI Agents SDK and SuperOptiX**

Give it a ⭐ if you find this helpful!

</div>
