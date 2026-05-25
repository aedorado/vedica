from .yoga_category import YogaCategory
from .yoga_type import YogaType

from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass(kw_only=True)
class VedicYoga:
    """
    Base class representing a detected Vedic Yoga with detailed information.
    
    Attributes:
        category: Category of yoga (Raja, Dhana, etc.)
        yoga_type: Type of formation (conjunction, aspect, exchange)
        primary_planet: Main planet involved in the yoga
        secondary_planet: Secondary planet (if applicable)
        primary_house: Primary house involved
        secondary_house: Secondary house (if applicable)
        strength_score: Numerical strength assessment (1-10)
        description: Detailed description of the yoga
        formation_details: Details about how the yoga is formed
        effects: Expected effects/results of the yoga
        additional_info: Any additional contextual information
    """
    category: YogaCategory
    yoga_type: YogaType
    primary_planet: str
    secondary_planet: str = ""
    primary_house: int = 0
    secondary_house: int = 0
    strength_score: float = 0.0
    description: str = ""
    formation_details: str = ""
    effects: str = ""
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate description and calculate strength after initialization."""
        if not self.description:
            self.description = self._generate_description()
        if self.strength_score == 0.0:
            self.strength_score = self._calculate_base_strength()
    
    def _generate_description(self) -> str:
        """Generate a human-readable description of the yoga."""
        return f"{self.category.value}: {self.primary_planet} forms {self.yoga_type.value.lower()}"
    
    def _calculate_base_strength(self) -> float:
        """Calculate base strength of the yoga (to be overridden by specific yoga types)."""
        return 5.0
