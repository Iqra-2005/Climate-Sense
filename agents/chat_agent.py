"""
Climate Advisor Chat Agent - Conversational AI
Provides context-aware climate guidance through chat interface.
"""

import os
import google.genai as genai
from typing import List, Dict, Optional


class ClimateChatAgent:
    """
    Conversational agent that remembers user's footprint profile.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the chat agent.
        
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
    
    def chat(
        self,
        user_message: str,
        footprint_profile: Dict,
        chat_history: List[Dict[str, str]],
        current_challenge: Optional[str] = None
    ) -> str:
        """
        Generate contextual response based on user message and profile.
        
        Args:
            user_message: User's chat message
            footprint_profile: User's footprint data
            chat_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            current_challenge: Currently selected One-Change Challenge
            
        Returns:
            Assistant's response
        """
        from config.prompts import CHAT_SYSTEM_PROMPT, CHAT_USER_TEMPLATE
        
        # Extract profile info
        top_drivers = [
            item['category'] 
            for item in footprint_profile.get('breakdown', [])[:3]
        ]
        
        from agents.estimator import CarbonEstimator
        estimator = CarbonEstimator()
        level, _ = estimator.get_footprint_level(
            footprint_profile.get('total_score', 0)
        )
        
        # Format chat history
        history_text = self._format_chat_history(chat_history[-6:])  # Last 6 messages
        
        # Build system context
        system_context = CHAT_SYSTEM_PROMPT.format(
            footprint_level=level,
            top_drivers=", ".join(top_drivers) if top_drivers else "Not analyzed yet",
            current_challenge=current_challenge or "None selected"
        )
        
        # Build user prompt
        user_prompt = CHAT_USER_TEMPLATE.format(
            user_message=user_message,
            chat_history=history_text
        )
        
        # Combine prompts
        full_prompt = f"{system_context}\n\n{user_prompt}"
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            raise RuntimeError(str(e))
    
    def _format_chat_history(self, history: List[Dict[str, str]]) -> str:
        """Format chat history for prompt."""
        if not history:
            return "No previous conversation."
        
        lines = []
        for msg in history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            lines.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(lines)
