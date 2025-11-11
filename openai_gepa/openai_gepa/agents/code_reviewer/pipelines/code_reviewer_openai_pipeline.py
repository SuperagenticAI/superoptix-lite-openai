"""
Code Reviewer Agent - Written using OpenAI Agents SDK patterns
This agent is written following the official OpenAI Agents SDK documentation
and then integrated with SuperOptiX for GEPA optimization.
"""

import asyncio
from typing import Dict, List, Optional
from pathlib import Path
import yaml
import json

from agents import Agent, Runner, OpenAIChatCompletionsModel
from openai import AsyncOpenAI


# ======================================================================
# Native OpenAI Agents SDK Implementation
# ======================================================================

class CodeReviewerAgent:
    """
    Code reviewer agent written using OpenAI Agents SDK patterns.
    This follows the official SDK documentation for creating agents.
    """

    def __init__(
        self,
        instructions: str,
        model: str = "gpt-oss:20b",
        api_base: str = "http://localhost:11434",
        temperature: float = 0.3
    ):
        """
        Initialize the code reviewer agent.

        Args:
            instructions: System instructions for the agent
            model: Model name (for Ollama, without 'ollama:' prefix)
            api_base: Ollama API base URL
            temperature: Model temperature
        """
        self.instructions = instructions

        # Initialize Ollama model using OpenAI Agents SDK
        self.model = OpenAIChatCompletionsModel(
            model=model,
            openai_client=AsyncOpenAI(
                base_url=f"{api_base}/v1",
                api_key="ollama",  # Ollama doesn't need real key
            ),
        )

        # Create the agent with instructions and model
        self.agent = Agent(
            name="Code Reviewer",
            instructions=instructions,
            model=self.model,
        )

        print(f"✅ Code Reviewer Agent initialized with Ollama: {model}")

    async def review_code(self, code: str, language: str = "unknown") -> str:
        """
        Review code and provide feedback.

        Args:
            code: Code snippet to review
            language: Programming language

        Returns:
            Review feedback
        """
        # Create context with code and language
        context = f"Language: {language}\n\nCode to review:\n```{language}\n{code}\n```"

        # Run the agent using Runner (official OpenAI Agents SDK pattern)
        result = await Runner.run(self.agent, input=context)

        # Extract the final message content
        if hasattr(result, 'final_message'):
            if hasattr(result.final_message, 'content'):
                return result.final_message.content
            return str(result.final_message)
        elif hasattr(result, 'content'):
            return result.content
        else:
            return str(result)


# ======================================================================
# SuperOptiX Integration Layer
# ======================================================================

# Use minimal BaseComponent from superoptix_lite (included in this demo)
# For production, use: from superoptix.core.base_component import BaseComponent
from openai_gepa.superoptix_lite import BaseComponent


class CodeReviewerComponent(BaseComponent):
    """
    SuperOptiX wrapper for the CodeReviewerAgent.
    This makes the native OpenAI SDK agent compatible with GEPA optimization.
    """

    def __init__(
        self,
        instructions: Optional[str] = None,
        model_config: Optional[Dict] = None,
        **kwargs
    ):
        """
        Initialize the component.

        Args:
            instructions: Agent instructions (optimizable by GEPA)
            model_config: Model configuration
            **kwargs: Additional config
        """
        # Default instructions
        default_instructions = self._build_default_instructions()

        # Initialize BaseComponent
        super().__init__(
            name="code_reviewer",
            description="AI code reviewer that analyzes code quality and suggests improvements",
            input_fields=["code", "language"],
            output_fields=["review"],
            variable=instructions or default_instructions,  # GEPA optimizes this!
            variable_type="instructions",
            framework="openai",
            config=model_config or {},
        )

        # Lazy initialization
        self._agent = None
        self._model_config = model_config or {}

    def _build_default_instructions(self) -> str:
        """Build default instructions from persona and constraints."""
        parts = []
        parts.append("Senior Code Reviewer")
        parts.append("\nRole: Code Quality Expert")
        parts.append("\nGoal: Provide constructive, actionable code review feedback that improves code quality")
        parts.append("\nBackstory: You are an experienced software engineer with 15+ years of experience reviewing code across multiple languages and paradigms. You understand best practices, design patterns, security vulnerabilities, and performance optimization. Your reviews are thorough yet constructive, focusing on teaching and improvement rather than criticism.")
        parts.append("\n\nReasoning Method: structured_analysis")
        parts.append("\nSteps:")
        parts.append("  1. Analyze code structure and readability")
        parts.append("  2. Identify potential bugs and edge cases")
        parts.append("  3. Check for security vulnerabilities")
        parts.append("  4. Evaluate performance implications")
        parts.append("  5. Suggest specific improvements")
        parts.append("\n\nConstraints:")
        parts.append("  - Focus on actionable feedback")
        parts.append("  - Prioritize critical issues over style preferences")
        parts.append("  - Provide specific examples and suggestions")
        parts.append("  - Be constructive and educational")

        return "\n".join(parts)

    def _initialize_agent(self):
        """Lazy initialization of the native OpenAI SDK agent."""
        if self._agent is not None:
            return

        # Extract model config
        model_str = self._model_config.get("model", "ollama:gpt-oss:20b")
        model_name = model_str.replace("ollama:", "")
        api_base = self._model_config.get("api_base", "http://localhost:11434")
        temperature = self._model_config.get("temperature", 0.3)

        # Create native OpenAI SDK agent
        self._agent = CodeReviewerAgent(
            instructions=self.variable,  # Use GEPA-optimizable variable
            model=model_name,
            api_base=api_base,
            temperature=temperature
        )

    async def run_async(self, code: str, language: str = "unknown") -> Dict[str, str]:
        """
        Run code review.

        Args:
            code: Code snippet to review
            language: Programming language

        Returns:
            Dict with 'review' key containing feedback
        """
        # Lazy initialize agent
        self._initialize_agent()

        # Run review using native agent
        review = await self._agent.review_code(code, language)

        return {"review": review}

    def run(self, code: str, language: str = "unknown") -> Dict[str, str]:
        """Sync wrapper for async run."""
        return asyncio.run(self.run_async(code, language))


# ======================================================================
# Factory Function
# ======================================================================

def create_code_reviewer_agent(
    instructions: Optional[str] = None,
    model_config: Optional[Dict] = None,
    **kwargs
) -> CodeReviewerComponent:
    """
    Factory function to create code reviewer agent.

    Args:
        instructions: Optional custom instructions (overrides default)
        model_config: Model configuration
        **kwargs: Additional configuration

    Returns:
        Initialized CodeReviewerComponent
    """
    return CodeReviewerComponent(
        instructions=instructions,
        model_config=model_config,
        **kwargs
    )


# ======================================================================
# SuperOptiX Pipeline - Full Workflow Support
# ======================================================================

class CodeReviewerPipeline:
    """
    SuperOptiX pipeline that provides full workflow support:
    - compile: Generate this code from playbook
    - evaluate: Run BDD scenarios
    - optimize: GEPA optimization
    - run: Execute agent
    """

    def __init__(self, playbook_path: str = None):
        """Initialize pipeline from playbook."""
        # Load playbook
        if playbook_path:
            with open(playbook_path) as f:
                playbook = yaml.safe_load(f)
                self.spec = playbook.get("spec", {})
                self.metadata = playbook.get("metadata", {})
        else:
            self.spec = {}
            self.metadata = {}

        # Get model config from spec
        model_config = {}
        if "language_model" in self.spec:
            lm = self.spec["language_model"]
            model_config = {
                "model": lm.get("model", "ollama:gpt-oss:20b"),
                "provider": lm.get("provider", "ollama"),
                "api_base": lm.get("api_base"),
                "temperature": lm.get("temperature"),
            }

        # Check for optimized weights
        optimized_instructions = None
        self.is_trained = False

        if playbook_path:
            # Try to load optimized weights from GEPA
            playbook_dir = Path(playbook_path).parent.parent
            optimized_dir = playbook_dir / "optimized"
            optimized_file = optimized_dir / "code_reviewer_openai_optimized.json"

            if optimized_file.exists():
                try:
                    with open(optimized_file) as f:
                        opt_data = json.load(f)
                        optimized_instructions = opt_data.get("best_variable")
                        best_score = opt_data.get("best_score", 0.0)

                    if optimized_instructions:
                        print(f"✅ Loaded optimized instructions (score: {best_score:.2%})")
                        self.is_trained = True
                except Exception as e:
                    print(f"⚠️  Failed to load optimization: {e}")

        # Create component (with optimized instructions if available)
        self.component = create_code_reviewer_agent(
            instructions=optimized_instructions,
            model_config=model_config
        )

        # Load BDD scenarios
        self.test_scenarios = self._load_bdd_scenarios()
        self.test_examples = self.test_scenarios  # Alias for CLI compatibility

    def _load_bdd_scenarios(self) -> List[Dict]:
        """Load BDD test scenarios from playbook."""
        scenarios = []

        if "feature_specifications" in self.spec:
            feature = self.spec["feature_specifications"]
            if "scenarios" in feature:
                for scenario in feature["scenarios"]:
                    scenarios.append({
                        "name": scenario.get("name", "Unnamed"),
                        "input": scenario.get("input", {}),
                        "expected_output": scenario.get("expected_output", {}),
                    })

        return scenarios

    async def run(self, code: str, language: str = "unknown") -> Dict[str, str]:
        """Run code review."""
        return await self.component.run_async(code=code, language=language)

    def evaluate(self) -> Dict:
        """
        Evaluate agent using BDD scenarios.
        Returns evaluation results.
        """
        print(f"\n🔍 Evaluating code_reviewer...\n")
        print(f"Testing {len(self.test_scenarios)} BDD scenarios:\n")

        results = []
        passed = 0
        failed = 0

        for scenario in self.test_scenarios:
            scenario_name = scenario.get("name", "Unnamed")

            try:
                # Get inputs and expected outputs
                inputs = scenario.get("input", {}) if isinstance(scenario, dict) else {}
                expected = scenario.get("expected_output", {}) if isinstance(scenario, dict) else {}

                # Run scenario (handle async properly!)
                result = asyncio.run(self.run(**inputs))

                # Check if output matches expected
                success = self._evaluate_output(result, expected)

                if success:
                    print(f"✅ {scenario_name}: PASS")
                    passed += 1
                else:
                    print(f"❌ {scenario_name}: FAIL")
                    failed += 1

                results.append({
                    "scenario": scenario_name,
                    "passed": success,
                    "output": result
                })

            except Exception as e:
                print(f"❌ {scenario_name}: ERROR - {e}")
                failed += 1
                results.append({
                    "scenario": scenario_name,
                    "passed": False,
                    "error": str(e)
                })

        # Calculate pass rate
        total = passed + failed
        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"\n{'='*60}")
        print(f"Overall: {passed}/{total} PASS ({pass_rate:.1f}%)")
        print(f"{'='*60}\n")

        return {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": pass_rate,
            "results": results
        }

    def _evaluate_output(self, result: Dict, expected: Dict) -> bool:
        """
        Evaluate if output matches expected criteria.
        Uses keyword matching for BDD scenarios.
        """
        import types

        # Convert SimpleNamespace to dict if needed
        if isinstance(result, types.SimpleNamespace):
            result = vars(result)
        if isinstance(expected, types.SimpleNamespace):
            expected = vars(expected)

        # Ensure we have dicts
        if not isinstance(result, dict):
            result = {"review": str(result)}
        if not isinstance(expected, dict):
            expected = {}

        # Simple keyword matching
        result_str = str(result).lower()
        expected_keywords = expected.get("expected_keywords", [])

        if expected_keywords:
            # Convert all keywords to strings and lowercase
            keywords_str = [str(kw).lower() for kw in expected_keywords if kw]
            matches = sum(1 for kw in keywords_str if kw in result_str)
            return matches >= len(keywords_str) * 0.5  # 50% threshold

        # If no keywords, consider it a pass
        return True


# ======================================================================
# CLI Entry Points
# ======================================================================

if __name__ == "__main__":
    # Example usage
    pipeline = CodeReviewerPipeline(
        playbook_path="openai_gepa/agents/code_reviewer/playbook/code_reviewer_playbook.yaml"
    )

    # Test with a sample
    code_sample = """
def get_user(username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return db.execute(query)
"""

    result = asyncio.run(pipeline.run(code=code_sample, language="python"))
    print(result["review"])
