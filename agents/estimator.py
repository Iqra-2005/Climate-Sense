"""
Carbon Estimation Agent - Rule-Based, Transparent Scoring System
Provides explainable carbon footprint estimates based on lifestyle inputs.
"""

from typing import Dict, List, Tuple


class CarbonEstimator:
    """
    Rule-based carbon footprint estimator.
    Uses transparent scoring system for explainability.
    """
    
    # Scoring weights for each category (higher = more impact)
    WEIGHTS = {
        'transport_mode': {
            'Car': 30,
            'Public': 10,
            'Bike': 2,
            'EV': 8
        },
        'vehicle_distance': {
            'Low': 5,
            'Medium': 15,
            'High': 25
        },
        'electricity': {
            'Low': 8,
            'Medium': 15,
            'High': 25
        },
        'diet': {
            'Veg': 5,
            'Mixed': 15,
            'Non-Veg': 25
        },
        'air_travel': {
            'Never': 0,
            'Rare': 10,
            'Frequent': 30
        },
        'waste': {
            'Low': 5,
            'Medium': 12,
            'High': 20
        },
        'recycling': {
            'Yes': -5,  # Negative weight reduces footprint
            'No': 0
        },
        'device_usage': {
            'Low': 3,
            'Medium': 8,
            'High': 15
        }
    }
    
    # Category labels for display
    CATEGORY_LABELS = {
        'transport_mode': 'Transport Mode',
        'vehicle_distance': 'Vehicle Distance',
        'electricity': 'Electricity Usage',
        'diet': 'Diet Type',
        'air_travel': 'Air Travel',
        'waste': 'Waste Generation',
        'recycling': 'Recycling Habits',
        'device_usage': 'Device Usage'
    }
    
    def __init__(self):
        """Initialize the carbon estimator."""
        pass
    
    def estimate_footprint(self, user_inputs: Dict[str, str]) -> Dict:
        """
        Estimate carbon footprint based on user lifestyle inputs.
        
        Args:
            user_inputs: Dictionary with keys matching WEIGHTS categories
            
        Returns:
            Dictionary containing:
                - total_score: Total footprint score
                - category_scores: Individual category contributions
                - category_percentages: Percentage contribution of each category
                - breakdown: Detailed breakdown for display
        """
        category_scores = {}
        
        # Calculate score for each category
        for category, value in user_inputs.items():
            if category in self.WEIGHTS and value in self.WEIGHTS[category]:
                category_scores[category] = self.WEIGHTS[category][value]
            else:
                category_scores[category] = 0
        
        # Calculate total score
        total_score = sum(category_scores.values())
        
        # Ensure minimum score of 1 to avoid division by zero
        if total_score <= 0:
            total_score = 1
        
        # Calculate percentage contributions
        category_percentages = {
            cat: (score / total_score) * 100 
            for cat, score in category_scores.items()
        }
        
        # Create breakdown for display
        breakdown = []
        for category, score in sorted(
            category_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        ):
            if score > 0:  # Only include categories with positive impact
                breakdown.append({
                    'category': self.CATEGORY_LABELS.get(category, category),
                    'score': score,
                    'percentage': category_percentages[category],
                    'value': user_inputs.get(category, 'N/A')
                })
        
        return {
            'total_score': total_score,
            'category_scores': category_scores,
            'category_percentages': category_percentages,
            'breakdown': breakdown,
            'raw_inputs': user_inputs
        }
    
    def get_footprint_level(self, total_score: float) -> Tuple[str, str]:
        """
        Categorize footprint into levels.
        
        Returns:
            Tuple of (level_name, description)
        """
        if total_score < 50:
            return ("Low", "Your lifestyle has a relatively low carbon impact. Great job!")
        elif total_score < 100:
            return ("Medium", "Your carbon footprint is moderate. There's room for improvement.")
        elif total_score < 150:
            return ("High", "Your lifestyle has a significant carbon impact. Let's work on reducing it.")
        else:
            return ("Very High", "Your carbon footprint is quite high. Every change matters!")
    
    def get_disclaimer(self) -> str:
        """Return disclaimer text for estimates."""
        return (
            "⚠️ **Disclaimer**: This is an indicative estimate for awareness and guidance, "
            "not a scientific measurement. Actual carbon footprints depend on many factors "
            "including location, energy sources, and specific consumption patterns."
        )
