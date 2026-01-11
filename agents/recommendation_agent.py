"""
Recommendation Prioritization Agent - LLM Decision-Making
Prioritizes actions by impact vs feasibility using LLM reasoning.
"""

import os
import google.genai as genai
from typing import Dict, List


class RecommendationAgent:
    """
    Uses LLM to prioritize recommendations based on impact and feasibility.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the recommendation agent.
        
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
    
    def prioritize_recommendations(
        self, 
        footprint_data: Dict,
        analysis_text: str
    ) -> str:
        """
        Generate prioritized recommendations based on footprint and analysis.
        
        Args:
            footprint_data: Output from CarbonEstimator.estimate_footprint()
            analysis_text: Output from ImpactAnalysisAgent.analyze()
            
        Returns:
            Formatted recommendations with prioritization
        """
        from config.prompts import RECOMMENDATION_PROMPT
        
        # Extract top drivers
        top_drivers = [
            item['category'] 
            for item in footprint_data['breakdown'][:3]
        ]
        
        # Create lifestyle summary
        lifestyle_summary = self._create_lifestyle_summary(footprint_data)
        
        # Get footprint level
        from agents.estimator import CarbonEstimator
        estimator = CarbonEstimator()
        level, _ = estimator.get_footprint_level(footprint_data['total_score'])
        
        # Build prompt
        prompt = RECOMMENDATION_PROMPT.format(
            top_drivers=", ".join(top_drivers),
            lifestyle_summary=lifestyle_summary,
            level=level
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
                raise RuntimeError(str(e))
    
    def _create_lifestyle_summary(self, footprint_data: Dict) -> str:
        """Create a concise lifestyle summary from footprint data."""
        inputs = footprint_data['raw_inputs']
        summary_parts = []
        
        if 'transport_mode' in inputs:
            summary_parts.append(f"Transport: {inputs['transport_mode']}")
        if 'diet' in inputs:
            summary_parts.append(f"Diet: {inputs['diet']}")
        if 'electricity' in inputs:
            summary_parts.append(f"Electricity: {inputs['electricity']}")
        if 'air_travel' in inputs:
            summary_parts.append(f"Air Travel: {inputs['air_travel']}")
        
        return "; ".join(summary_parts)
