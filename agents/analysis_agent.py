"""
Impact Analysis Agent - LLM-Based Reasoning
Analyzes carbon footprint breakdown and explains top emission drivers.
"""

import os
import google.genai as genai
from typing import Dict


class ImpactAnalysisAgent:
    """
    Uses LLM to analyze footprint breakdown and provide natural-language insights.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the impact analysis agent.
        
        Args:
            api_key: Gemini API key (if None, reads from environment)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Set GEMINI_API_KEY environment variable."
            )
        
        # Using new google.genai Client API
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'models/gemini-2.5-flash'
    
    def analyze(self, footprint_data: Dict) -> str:
        """
        Analyze footprint breakdown and provide insights.
        
        Args:
            footprint_data: Output from CarbonEstimator.estimate_footprint()
            
        Returns:
            Natural language analysis of the footprint
        """
        from config.prompts import IMPACT_ANALYSIS_PROMPT
        
        # Format breakdown for prompt
        breakdown_text = self._format_breakdown(footprint_data['breakdown'])
        
        # Get footprint level
        from agents.estimator import CarbonEstimator
        estimator = CarbonEstimator()
        level, level_desc = estimator.get_footprint_level(
            footprint_data['total_score']
        )
        
        # Build prompt
        prompt = IMPACT_ANALYSIS_PROMPT.format(
            breakdown=breakdown_text,
            total_score=footprint_data['total_score'],
            level=level,
            level_description=level_desc
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            raise RuntimeError(str(e))

    
    def _format_breakdown(self, breakdown: list) -> str:
        """Format breakdown list into readable text."""
        lines = []
        for item in breakdown:
            lines.append(
                f"- {item['category']}: {item['value']} "
                f"(Score: {item['score']:.1f}, {item['percentage']:.1f}% of total)"
            )
        return "\n".join(lines)
