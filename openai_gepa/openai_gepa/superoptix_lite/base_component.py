"""
Minimal BaseComponent for OpenAI Agents SDK integration

This is a simplified version of SuperOptiX's BaseComponent for demonstration.
It provides the minimal interface needed for GEPA optimization compatibility.

For production use, install the full SuperOptiX framework.
"""

from typing import Any, Dict, Optional


class BaseComponent:
    """
    Base component class for agent optimization.

    This minimal implementation provides the interface needed to integrate
    OpenAI Agents SDK agents with GEPA-style optimization.

    Attributes:
        name: Component identifier
        variable: The optimizable variable (e.g., instructions, system prompt)
        variable_type: Type of variable being optimized
        framework: Target framework (e.g., "openai", "dspy", "crewai")
    """

    def __init__(
        self,
        name: str = "component",
        variable: Optional[str] = None,
        variable_type: str = "instructions",
        framework: str = "openai",
        **kwargs
    ):
        """
        Initialize the base component.

        Args:
            name: Component name
            variable: The optimizable variable (instructions/prompt)
            variable_type: Type of variable ("instructions", "system_prompt", etc.)
            framework: Framework name ("openai", "dspy", "crewai", etc.)
            **kwargs: Additional framework-specific parameters
        """
        self.name = name
        self._variable = variable
        self.variable_type = variable_type
        self.framework = framework
        self.config = kwargs

    @property
    def variable(self) -> Optional[str]:
        """Get the current optimizable variable."""
        return self._variable

    @variable.setter
    def variable(self, value: str):
        """
        Set the optimizable variable.

        This is called by GEPA during optimization to test different variations.
        """
        self._variable = value

    def forward(self, **inputs) -> Dict[str, Any]:
        """
        Execute the agent with given inputs.

        This method should be overridden by subclasses to implement
        the actual agent execution logic.

        Args:
            **inputs: Input parameters for the agent

        Returns:
            Dictionary with agent outputs
        """
        raise NotImplementedError(
            "Subclasses must implement forward() method"
        )

    def update(self, new_variable: str):
        """
        Update the optimizable variable.

        Called by GEPA to update the agent with improved instructions.
        Subclasses may override this to handle reinitialization.

        Args:
            new_variable: New value for the optimizable variable
        """
        self.variable = new_variable

    def __call__(self, **inputs) -> Dict[str, Any]:
        """Allow component to be called directly."""
        return self.forward(**inputs)

    def __repr__(self) -> str:
        """String representation of the component."""
        return (
            f"{self.__class__.__name__}("
            f"name={self.name}, "
            f"framework={self.framework}, "
            f"variable_type={self.variable_type})"
        )
