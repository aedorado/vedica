from .vedic_yoga import VedicYoga
from .yoga_category import YogaCategory
from .yoga_type import YogaType

from dataclasses import dataclass

@dataclass
class DhanaYoga(VedicYoga):
    """Specialized class for Dhana (Wealth) Yogas."""
    
    def __post_init__(self):
        self.category = YogaCategory.DHANA_YOGA
        super().__post_init__()
    
    def _generate_description(self) -> str:
        """Generate description specific to Dhana Yoga."""
        house_descriptions = {
            1: "Lagna (Self)",
            2: "Wealth/Family", 
            5: "Intelligence/Speculation",
            9: "Fortune/Luck",
            11: "Gains/Income"
        }
        
        primary_desc = house_descriptions.get(self.primary_house, f"{self.primary_house}th house")
        
        # Handle case where secondary_planet might be empty (for placement yogas)
        if not self.secondary_planet:
            conjunction_info = ""
            if self.yoga_type == YogaType.CONJUNCTION and 'conjunction_house' in self.additional_info:
                conjunction_info = f" in {self.additional_info['conjunction_house']}th house"
            elif self.yoga_type == YogaType.HOUSE_PLACEMENT and self.secondary_house:
                secondary_desc = house_descriptions.get(self.secondary_house, f"{self.secondary_house}th house")
                return (f"Dhana Yoga: {self.primary_planet} (lord of {primary_desc}) "
                        f"placed favorably in {secondary_desc}")
            
            return (f"Dhana Yoga: {self.primary_planet} (lord of {primary_desc}) "
                    f"creates wealth combination through {self.yoga_type.value.lower()}{conjunction_info}")
        
        # Normal case with both planets
        secondary_desc = house_descriptions.get(self.secondary_house, f"{self.secondary_house}th house")
        
        conjunction_info = ""
        if self.yoga_type == YogaType.CONJUNCTION and 'conjunction_house' in self.additional_info:
            conjunction_info = f" in {self.additional_info['conjunction_house']}th house"
        
        return (f"Dhana Yoga: {self.primary_planet} (lord of {primary_desc}) "
                f"and {self.secondary_planet} (lord of {secondary_desc}) "
                f"create wealth combination through {self.yoga_type.value.lower()}{conjunction_info}")
    
    def _calculate_base_strength(self) -> float:
        """Calculate strength specific to Dhana Yoga."""
        base_strength = 5.0
        
        # Primary wealth houses (2nd and 11th) get higher strength
        if self.primary_house in [2, 11] or self.secondary_house in [2, 11]:
            base_strength += 1.5
        
        # Lagna involvement is always powerful
        if self.primary_house == 1 or self.secondary_house == 1:
            base_strength += 1.5
        
        # 5th and 9th house combinations (trikona wealth)
        if self.primary_house in [5, 9] or self.secondary_house in [5, 9]:
            base_strength += 1.0
        
        # Conjunction is strongest for wealth yogas
        if self.yoga_type == YogaType.CONJUNCTION:
            base_strength += 1.2
        elif self.yoga_type == YogaType.SIGN_EXCHANGE:
            base_strength += 0.8
        elif self.yoga_type == YogaType.MUTUAL_ASPECT:
            base_strength += 0.6
        
        # Placement in wealth houses
        if 'conjunction_house' in self.additional_info:
            conj_house = self.additional_info['conjunction_house']
            if conj_house in [1, 2, 5, 9, 11]:
                base_strength += 0.5
        
        return min(base_strength, 10.0)
