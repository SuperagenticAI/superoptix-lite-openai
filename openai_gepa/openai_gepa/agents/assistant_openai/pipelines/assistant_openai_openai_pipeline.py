"""
AssistantOpenai Agent - OpenAI Agents SDK Implementation

Auto-generated from SuperSpec playbook using SuperOptiX compiler.
Framework: OpenAI Agents SDK
Generated: 2025-11-10 20:52:19

SuperSpec Metadata:
  Name: assistant_openai
  Version: 1.0.0
  Description: Simple Q&A assistant built with OpenAI Agents SDK, optimized for Ollama local models
  Framework: OpenAI Agents SDK
"""

from typing import List, Dict, Any, Optional
import asyncio

# OpenAI Agents SDK imports
try:
	from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel
	from openai import AsyncOpenAI
	OPENAI_AGENTS_AVAILABLE = True
except ImportError as e:
	OPENAI_AGENTS_AVAILABLE = False
	print(f"⚠️  OpenAI Agents SDK not available: {e}")
	print("⚠️  Install with: pip install openai-agents")

# Use minimal BaseComponent from superoptix_lite (included in this demo)
# For production, use: from superoptix.core.base_component import BaseComponent
from openai_gepa.superoptix_lite import BaseComponent


class AssistantOpenaiComponent(BaseComponent):
	"""
	BaseComponent wrapper for OpenAI Agents SDK - Simple Q&A assistant built with OpenAI Agents SDK, optimized for Ollama local models
	
	This component wraps an OpenAI Agent and makes it compatible with 
	SuperOptiX's Universal GEPA optimizer.
	
	Optimizable Variable: instructions (the agent's system prompt)
	
	Framework: OpenAI Agents SDK
	Input: Any field from input_fields
	Output: Any field from output_fields
	"""
	
	def __init__(
		self,
		instructions: Optional[str] = None,
		model_config: Optional[Dict] = None,
		tools: Optional[List] = None,
		**kwargs
	):
		"""
		Initialize OpenAI Agent component.
		
		Args:
			instructions: Agent instructions (system prompt) - optimizable by GEPA!
			model_config: Model configuration dict
			tools: List of tools for the agent
			**kwargs: Additional configuration
		"""
		# Default instructions from playbook
		default_instructions = self._build_default_instructions()
		
		# Initialize BaseComponent
		super().__init__(
			name="assistant_openai",
			description="""Simple Q&A assistant built with OpenAI Agents SDK, optimized for Ollama local models""",
			input_fields=["query"],
			output_fields=["response"],
			variable=instructions or default_instructions,  # GEPA optimizes this!
			variable_type="instructions",
			framework="openai",
			config=model_config or {},
		)
		
		# Store tools
		self._tools = tools or []
		
		# Lazy initialization
		self._agent = None
		self._model = None
	
	def _build_default_instructions(self) -> str:
		"""Build default instructions from playbook."""
		instructions_parts = []
		instructions_parts.append("Helpful AI Assistant")
		instructions_parts.append("\\nGoal: " + "Provide clear, concise, and helpful responses to user queries")
		instructions_parts.append("\\nBackstory: " + "You are a friendly and knowledgeable AI assistant designed to help users with questions, explanations, and general information. You excel at breaking down complex topics into understandable answers. ")
		instructions_parts.append("\\n\\nReasoning Method: " + "direct")
		instructions_parts.append("\\nSteps to follow:")
		instructions_parts.append("  1. " + "Understand the user\u0027s question")
		instructions_parts.append("  2. " + "Provide a clear and helpful answer")
		instructions_parts.append("  3. " + "Be concise but complete")
		instructions_parts.append("\\n\\nConstraints:")
		instructions_parts.append("  - " + "Keep responses concise")
		instructions_parts.append("  - " + "Be factual and accurate")
		instructions_parts.append("  - " + "Ask for clarification if needed")
		
		if not instructions_parts:
			return "You are a helpful AI assistant."
		
		return "\\n".join(instructions_parts)
	
	def _initialize_model(self):
		"""Initialize the model (Ollama or OpenAI)."""
		if self._model is not None:
			return

		# Convert config to dict if needed
		import types
		config = vars(self.config) if isinstance(self.config, types.SimpleNamespace) else self.config
		if not isinstance(config, dict):
			config = {}

		model_str = config.get("model", "ollama:llama3.1:8b")
		self._actual_model_name = model_str  # Store for display

		# Check if using Ollama
		if model_str.startswith("ollama:") or "ollama" in config.get("provider", "").lower():
			# Extract model name
			model_name = model_str.replace("ollama:", "")
			api_base = config.get("api_base", "http://localhost:11434")

			# Use OpenAIChatCompletionsModel with Ollama
			self._model = OpenAIChatCompletionsModel(
				model=model_name,
				openai_client=AsyncOpenAI(
					base_url=f"{api_base}/v1",
					api_key="ollama",  # Ollama doesn't need real key
				),
			)
			print(f"✅ OpenAI Agents SDK initialized with Ollama: {model_name}")
		else:
			# Use default OpenAI model (or None to use SDK default)
			self._model = model_str if model_str != "ollama:llama3.1:8b" else None
			print(f"✅ OpenAI Agents SDK initialized with model: {model_str}")
	
	def _initialize_agent(self):
		"""Lazy initialization of OpenAI Agent."""
		if self._agent is not None:
			return
		
		if not OPENAI_AGENTS_AVAILABLE:
			raise ImportError("OpenAI Agents SDK not installed. Install with: pip install openai-agents")
		
		# Initialize model first
		self._initialize_model()
		
		# Create OpenAI Agent with current configuration
		self._agent = Agent(
			name="assistant_openai",
			instructions=self.variable,  # This gets optimized by GEPA!
			tools=self._tools,
			model=self._model,
		)
	
	async def forward(self, **inputs: Any) -> Dict[str, Any]:
		"""
		Execute the OpenAI Agent.
		
		Args:
			**inputs: Input fields from playbook
		
		Returns:
			Dict with output fields
		"""
		# Ensure agent is initialized
		self._initialize_agent()
		
		# Get the input query/text
		input_text = inputs.get("query", "")
		
		# Run agent asynchronously (avoid event loop conflicts)
		try:
			result = await Runner.run(self._agent, input=input_text)
			
			# Extract final output
			response = result.final_output if hasattr(result, 'final_output') else str(result)
			
			return {"response": response}
		
		except Exception as e:
			import traceback
			error_msg = f"Error executing agent: {str(e)}"
			print(f"⚠️  {error_msg}")
			traceback.print_exc()
			return {"response": f"Error: {str(e)}"}
	
	def update(self, new_variable: Any) -> None:
		"""
		Update instructions (called by GEPA optimizer during optimization).
		
		Args:
			new_variable: New instructions text
		"""
		super().update(new_variable)
		# Force re-initialization with new instructions
		self._agent = None
	
	def __repr__(self) -> str:
		return (
			f"AssistantOpenaiComponent("
			f"framework=openai, "
			f"optimizable={self.optimizable})"
		)


# ======================================================================
# Factory Function
# ======================================================================

def create_assistant_openai_agent(
	instructions: Optional[str] = None,
	model_config: Optional[Dict] = None,
	**kwargs
) -> AssistantOpenaiComponent:
	"""
	Factory function to create assistant_openai agent.
	
	Args:
		instructions: Optional custom instructions (overrides default)
		model_config: Model configuration
		**kwargs: Additional configuration
	
	Returns:
		Initialized AssistantOpenaiComponent
	"""
	tools = []  # Tools can be added here
	
	return AssistantOpenaiComponent(
		instructions=instructions,
		model_config=model_config,
		tools=tools,
		**kwargs
	)


# ======================================================================
# AssistantOpenaiPipeline - SuperOptiX Workflow Support
# ======================================================================

import yaml
from pathlib import Path
from typing import List, Dict, Any


class AssistantOpenaiPipeline:
	"""
	OpenAI Agents SDK pipeline with full SuperOptiX workflow support.
	
	Supports:
	- compile: Generate this code from playbook
	- evaluate: Run BDD scenarios
	- optimize: GEPA optimization  
	- run: Execute agent
	
	This makes OpenAI Agents SDK work with standard SuperOptiX commands!
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
				"model": lm.get("model", "ollama:llama3.1:8b"),
				"provider": lm.get("provider", "ollama"),
				"api_base": lm.get("api_base"),
				"temperature": lm.get("temperature"),
			}

		# Check for optimized weights
		optimized_instructions = None
		self.is_trained = False

		if playbook_path:
			# Try to load optimized weights from GEPA
			import os
			import json

			# Build path to optimized file
			playbook_dir = Path(playbook_path).parent.parent
			optimized_dir = playbook_dir / "optimized"
			optimized_file = optimized_dir / "assistant_openai_openai_optimized.json"

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
		self.component = create_assistant_openai_agent(
			instructions=optimized_instructions,
			model_config=model_config
		)

		# Load BDD scenarios
		self.test_scenarios = self._load_bdd_scenarios()

		# Alias for CLI compatibility
		self.test_examples = self.test_scenarios
	
	def _load_bdd_scenarios(self) -> List[Dict]:
		"""Load BDD test scenarios from playbook."""
		scenarios = []
		feature_specs = self.spec.get("feature_specifications", {})
		scenario_list = feature_specs.get("scenarios", [])
		
		for scenario in scenario_list:
			scenarios.append({
				"name": scenario.get("name", "Unnamed"),
				"description": scenario.get("description", ""),
				"input": scenario.get("input", {}),
				"expected_output": scenario.get("expected_output", {}),
			})
		
		return scenarios
	
	async def run(self, **inputs) -> Dict[str, Any]:
		"""
		Execute agent (unified interface for SuperOptiX CLI).
		
		Args:
			**inputs: Input fields (e.g., query="...", text="...")
		
		Returns:
			Dict with output fields
		"""
		# Use component's forward method (async)
		result = await self.component.forward(**inputs)
		return result
	
	def evaluate(self) -> Dict[str, Any]:
		"""
		Evaluate agent with BDD scenarios.

		Returns:
			Dict with evaluation results
		"""
		if not self.test_scenarios:
			print("⚠️  No BDD scenarios found in playbook")
			return {"pass": 0, "fail": 0, "pass_rate": 0.0}

		print(f"\n🔍 Evaluating assistant_openai...\n")
		print(f"Testing {len(self.test_scenarios)} BDD scenarios:\n")

		passed = 0
		failed = 0
		results = []

		for scenario in self.test_scenarios:
			# Convert SimpleNamespace to dict if needed
			import types
			if isinstance(scenario, types.SimpleNamespace):
				scenario = vars(scenario)

			scenario_name = scenario.get("name", "Unnamed") if isinstance(scenario, dict) else "Unnamed"

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
					"output": result,
				})

			except Exception as e:
				import traceback
				print(f"❌ {scenario_name}: ERROR - {e}")
				traceback.print_exc()
				failed += 1
				results.append({
					"scenario": scenario_name,
					"passed": False,
					"error": str(e),
				})

		pass_rate = passed / len(self.test_scenarios) if self.test_scenarios else 0.0

		print(f"\n{'='*60}")
		print(f"Overall: {passed}/{len(self.test_scenarios)} PASS ({pass_rate*100:.1f}%)")
		print(f"{'='*60}\n")

		return {
			"pass": passed,
			"fail": failed,
			"total": len(self.test_scenarios),
			"pass_rate": pass_rate,
			"results": results,
		}
	
	def _evaluate_output(self, result: Dict, expected: Dict) -> bool:
		"""Check if result matches expected output."""
		# Convert SimpleNamespace to dict if needed
		import types
		if isinstance(result, types.SimpleNamespace):
			result = vars(result)
		if isinstance(expected, types.SimpleNamespace):
			expected = vars(expected)
		
		# Ensure we have dicts
		if not isinstance(result, dict):
			result = {"response": str(result)}
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
		
		# Check response field
		if "response" in expected and "response" in result:
			return expected["response"].lower() in result["response"].lower()
		
		return True  # Pass if no clear criteria
	
	def run_bdd_test_suite(
		self, auto_tune: bool = False, ignore_checks: bool = False
	) -> Dict[str, Any]:
		"""
		Run BDD test suite (CLI compatibility method).
		
		This method is called by the CLI evaluate command and wraps the 
		standard evaluate() method to format results for CLI display.
		
		Args:
			auto_tune: Whether to automatically optimize based on results (unused)
			ignore_checks: If True, treats all scenarios as passed
		
		Returns:
			Dict containing test results formatted for CLI
		"""
		if not self.test_examples:
			return {
				"success": False,
				"message": "No BDD specifications defined in feature_specifications",
				"summary": {"total": 0, "passed": 0, "failed": 0, "pass_rate": "0.00%"},
				"bdd_results": {"detailed_results": []},
				"model_analysis": {},
				"recommendations": [],
			}
		
		# Run evaluation
		eval_results = self.evaluate()
		
		# Convert to CLI format
		detailed_results = []
		for result in eval_results.get("results", []):
			passed = result.get("passed", False)
			if ignore_checks:
				passed = True
			
			detailed_results.append({
				"scenario_name": result.get("scenario", "Unnamed"),
				"description": result.get("description", ""),
				"passed": passed,
				"confidence_score": 1.0 if passed else 0.0,
				"actual_output": result.get("output", {}),
			})
		
		# Calculate metrics
		total = eval_results.get("total", 0)
		passed = eval_results.get("pass", 0) if not ignore_checks else total
		failed = total - passed
		pass_rate = eval_results.get("pass_rate", 0.0) * 100
		
		return {
			"success": True,
			"summary": {
				"total": total,
				"passed": passed,
				"failed": failed,
				"pass_rate": f"{pass_rate:.1f}%",
			},
			"bdd_results": {
				"detailed_results": detailed_results,
				"total_scenarios": total,
				"scenarios_passed": passed,
				"scenarios_failed": failed,
				"pass_rate": f"{pass_rate:.1f}%",
				"bdd_score": pass_rate / 100,
			},
			"model_analysis": {
				"framework": "OpenAI Agents SDK",
				"model": "ollama:gpt-oss:20b",
			},
			"recommendations": [],
		}
	
	def optimize_with_gepa(
		self,
		auto: str = "medium",
		metric: str = "response_accuracy",
	) -> Dict[str, Any]:
		"""
		Optimize agent with GEPA.

		NOTE: This demo includes a custom optimization script.
		Please use: python optimize_code_reviewer.py

		For production use with full GEPA, install SuperOptiX:
		    pip install superoptix[frameworks-openai]

		Args:
			auto: Optimization budget ("light", "medium", "heavy")
			metric: Metric to optimize

		Returns:
			Optimization results
		"""
		print("\n" + "="*80)
		print("⚠️  GEPA Optimization")
		print("="*80)
		print()
		print("This demo includes a custom optimization script.")
		print()
		print("To optimize this agent, run:")
		print("    python optimize_code_reviewer.py")
		print()
		print("For production use with full SuperOptiX GEPA:")
		print("    pip install superoptix[frameworks-openai]")
		print()
		print("="*80)

		return {
			"message": "Use optimize_code_reviewer.py script for optimization",
			"script": "optimize_code_reviewer.py"
		}


# ======================================================================
# Main Execution
# ======================================================================

if __name__ == "__main__":
	"""
	Test the pipeline directly.
	
	Usage:
		python assistant_openai_pipeline.py
	"""
	print("🧪 Testing assistant_openai Pipeline\n")
	
	# Find playbook
	playbook_path = Path(__file__).parent.parent / "playbook" / "assistant_openai_playbook.yaml"
	
	if not playbook_path.exists():
		print(f"❌ Playbook not found: {playbook_path}")
		print("💡 Run from agent directory or compile with: super agent compile assistant_openai")
		exit(1)
	
	# Initialize pipeline
	pipeline = AssistantOpenaiPipeline(playbook_path=str(playbook_path))
	
	# Test run
	print("🚀 Testing agent execution...\n")
	test_result = pipeline.run(query="Hello! How can you help me?")
	print(f"Result: {test_result}\n")
	
	# Evaluate if scenarios available
	if pipeline.test_scenarios:
		print("🧪 Running evaluation...\n")
		eval_result = pipeline.evaluate()
		print(f"\nEvaluation: {eval_result['pass']}/{eval_result['total']} passed")

