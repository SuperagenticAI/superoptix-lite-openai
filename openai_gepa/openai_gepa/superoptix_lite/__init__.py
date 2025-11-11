"""
SuperOptiX Lite - Minimal components for standalone demo

This package contains minimal implementations of SuperOptiX components needed
for the OpenAI Agents SDK + GEPA demo. These are simplified versions for
demonstration purposes.

For production use, install the full SuperOptiX framework:
    pip install superoptix[frameworks-openai]
"""

from openai_gepa.superoptix_lite.base_component import BaseComponent

__all__ = ["BaseComponent"]
