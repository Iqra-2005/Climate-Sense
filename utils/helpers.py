"""
Helper utilities for ClimateSense application.
"""

import streamlit as st
from typing import Dict, Any, Tuple


def initialize_session_state():
    """Initialize all session state variables."""
    defaults = {
        'step': 0,
        'user_inputs': {},
        'footprint_data': None,
        'analysis_text': None,
        'recommendations_text': None,
        'challenge': None,
        'chat_history': [],
        'footprint_calculated': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session():
    """Reset session state for new calculation."""
    st.session_state.step = 0
    st.session_state.user_inputs = {}
    st.session_state.footprint_data = None
    st.session_state.analysis_text = None
    st.session_state.recommendations_text = None
    st.session_state.challenge = None
    st.session_state.chat_history = []
    st.session_state.footprint_calculated = False


def validate_inputs(user_inputs: Dict[str, str]) -> Tuple[bool, str]:
    """
    Validate user inputs.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = [
        'transport_mode',
        'vehicle_distance',
        'electricity',
        'diet',
        'air_travel',
        'waste',
        'recycling',
        'device_usage'
    ]
    
    for field in required_fields:
        if field not in user_inputs or not user_inputs[field]:
            return False, f"Please fill in all fields. Missing: {field}"
    
    return True, ""


def format_footprint_display(footprint_data: Dict) -> str:
    """Format footprint data for display."""
    if not footprint_data:
        return "No data available"
    
    level, level_desc = footprint_data.get('level', ('Unknown', ''))
    total_score = footprint_data.get('total_score', 0)
    
    return f"**Footprint Level**: {level}\n\n**Total Score**: {total_score:.1f}\n\n{level_desc}"
