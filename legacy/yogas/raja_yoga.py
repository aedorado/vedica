from .vedic_yoga import VedicYoga
from .yoga_category import YogaCategory
from .yoga_type import YogaType

from dataclasses import dataclass

import logging
logger = logging.getLogger(__name__)


@dataclass 
class RajaYoga(VedicYoga):
    """Specialized class for Raja Yogas."""
    
    def __post_init__(self):
        self.category = YogaCategory.RAJA_YOGA
        super().__post_init__()
    
    def _generate_description(self) -> str:
        """Generate description specific to Raja Yoga."""
        kendra_type = "Kendra"
        if self.primary_house == 1:
            kendra_type = "Kendra/Trikona"
        
        trikona_type = "Trikona"  
        if self.secondary_house == 1:
            trikona_type = "Kendra/Trikona"
        
        conjunction_info = ""
        if self.yoga_type == YogaType.CONJUNCTION and 'conjunction_house' in self.additional_info:
            conjunction_info = f" in {self.additional_info['conjunction_house']}th house"
        
        return (f"Raja Yoga: {self.primary_planet} (lord of {self.primary_house}th house - {kendra_type}) "
                f"and {self.secondary_planet} (lord of {self.secondary_house}th house - {trikona_type}) "
                f"form a powerful combination through {self.yoga_type.value.lower()}{conjunction_info}")
    
    def _calculate_base_strength(self) -> float:
        """Calculate strength specific to Raja Yoga."""
        base_strength = 5.0
        
        # Boost for specific house combinations
        if self.primary_house == 1 or self.secondary_house == 1:
            base_strength += 2.0  # Lagna involvement is powerful
        if self.primary_house == 10 or self.secondary_house == 9:
            base_strength += 1.5  # Career and dharma houses
        if self.primary_house == 4 or self.secondary_house == 5:
            base_strength += 1.0  # Home and creativity houses
        
        # Yoga type adjustments
        if self.yoga_type == YogaType.CONJUNCTION:
            base_strength += 1.0
        elif self.yoga_type == YogaType.SIGN_EXCHANGE:
            base_strength += 0.5
        
        # Same house conjunction gets extra strength
        if self.yoga_type == YogaType.CONJUNCTION and 'conjunction_house' in self.additional_info:
            base_strength += 0.5
        
        return min(base_strength, 10.0)
