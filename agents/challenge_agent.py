"""
One-Change Challenge Agent
Suggests specific, realistic weekly challenges for behavior change.
"""

import os
import google.genai as genai
from typing import Dict, Optional


class ChallengeAgent:
    """
    Generates personalized One-Change Challenges based on user profile.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the challenge agent.
        
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
    
    def suggest_challenge(
        self,
        footprint_data: Dict,
        recommendations_text: str
    ) -> Dict[str, str]:
        """
        Suggest a One-Change Challenge based on footprint and recommendations.
        
        Args:
            footprint_data: Output from CarbonEstimator.estimate_footprint()
            recommendations_text: Output from RecommendationAgent.prioritize_recommendations()
            
        Returns:
            Dictionary with challenge details:
                - title: Challenge title
                - description: What to do
                - impact: Why it matters
                - success_criteria: How to measure success
        """
        from config.prompts import CHALLENGE_PROMPT
        
        # Extract top drivers
        top_drivers = [
            item['category'] 
            for item in footprint_data['breakdown'][:3]
        ]
        
        # Extract immediate action from recommendations
        immediate_action = self._extract_immediate_action(recommendations_text)
        
        # Create lifestyle summary
        lifestyle_summary = self._create_lifestyle_summary(footprint_data)
        
        # Build prompt
        prompt = CHALLENGE_PROMPT.format(
            top_drivers=", ".join(top_drivers),
            immediate_action=immediate_action,
            lifestyle_summary=lifestyle_summary
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            challenge_text = response.text
            
            # Parse challenge into structured format
            return self._parse_challenge(challenge_text)
        except Exception as e:
                raise RuntimeError(str(e))
    
    def _extract_immediate_action(self, recommendations: str) -> str:
        """Extract immediate action from recommendations text."""
        # Try to find the immediate action section
        lines = recommendations.split('\n')
        immediate_section = []
        in_section = False
        
        for line in lines:
            if 'immediate' in line.lower() or 'low-effort' in line.lower():
                in_section = True
            elif in_section and line.strip() and not line.strip().startswith('**'):
                immediate_section.append(line.strip())
            elif in_section and line.strip().startswith('**') and 'medium' in line.lower():
                break
        
        if immediate_section:
            return ' '.join(immediate_section[:3])  # First few lines
        return "Focus on reducing top emission drivers"
    
    def _create_lifestyle_summary(self, footprint_data: Dict) -> str:
        """Create lifestyle summary."""
        inputs = footprint_data['raw_inputs']
        parts = []
        if 'transport_mode' in inputs:
            parts.append(f"Transport: {inputs['transport_mode']}")
        if 'diet' in inputs:
            parts.append(f"Diet: {inputs['diet']}")
        return "; ".join(parts)
    
    def _parse_challenge(self, challenge_text: str) -> Dict[str, str]:
        """Parse challenge text into structured format."""
        challenge = {
            'title': 'Your Climate Challenge',
            'description': challenge_text,
            'impact': 'Reducing your carbon footprint',
            'success_criteria': 'Complete the challenge for 7 days'
        }
        
        # Try to extract structured parts
        lines = challenge_text.split('\n')
        current_key = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if '**Challenge Title**' in line or 'title' in line.lower():
                current_key = 'title'
                # Extract title
                if ':' in line:
                    challenge['title'] = line.split(':', 1)[1].strip()
            elif '**What to do**' in line or 'what to do' in line.lower():
                current_key = 'description'
            elif '**Why it matters**' in line or 'why it matters' in line.lower():
                current_key = 'impact'
            elif '**Success criteria**' in line or 'success criteria' in line.lower():
                current_key = 'success_criteria'
            elif line.startswith('**') and line.endswith('**'):
                # New section header
                continue
            elif current_key:
                if challenge[current_key] == challenge_text:  # Still default
                    challenge[current_key] = line
                else:
                    challenge[current_key] += ' ' + line
        
        return challenge
