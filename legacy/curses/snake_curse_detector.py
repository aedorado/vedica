"""
Snake Curses Detection Module.

Detects curses from snakes based on specific planetary placements and conjunctions.
Reference: Vedic texts on Naga curse and snake-related afflictions.
"""

import logging
from typing import Dict, List, Optional
from .curse_detector_base import CurseDetectorBase, CurseRecord

logger = logging.getLogger(__name__)


class SnakeCurseDetector(CurseDetectorBase):
    """Detects curses from snakes based on planetary placements."""

    def __init__(self, planet_data_objs: Dict, house_data_objs: Dict):
        """
        Initialize Snake Curse Detector.
        
        Args:
            planet_data_objs: Dictionary of planet objects
            house_data_objs: Dictionary of house objects
        """
        super().__init__(planet_data_objs, house_data_objs)
        self.detected_curses: List[CurseRecord] = []

    def detect_curses(self) -> List[CurseRecord]:
        """Detect all snake curses."""
        logger.info("Detecting Snake Curses...")
        
        self._check_rahu_5h_aspected_by_mars()
        self._check_5l_rahu_ketu_axis_saturn_5h_moon()
        self._check_jupiter_rahu_5l_weak_ll_mars()
        
        return self.detected_curses

    def _check_rahu_5h_aspected_by_mars(self) -> None:
        """
        Check: Rahu in 5H aspected by Mars
        
        Rahu in 5H with Mars aspect creates snake curse affecting children and health.
        """
        rahu_in_5h = self.is_planet_in_house("Rahu", 5)
        if not rahu_in_5h:
            return

        # Check if Mars aspects Rahu (Mars aspects 4th, 7th, 8th from its position)
        mars_house = self.get_planet_house("Mars")
        if mars_house:
            mars_aspects = [
                (mars_house + 4 - 1) % 12 + 1,  # 4th aspect
                (mars_house + 7 - 1) % 12 + 1,  # 7th aspect (opposite)
                (mars_house + 8 - 1) % 12 + 1,  # 8th aspect
                mars_house  # own position
            ]
            mars_aspects_rahu = 5 in mars_aspects
        else:
            mars_aspects_rahu = False

        # Alternative: check if they're in same sign (simplified)
        mars_rahu_sign_aspect = (self.get_planet_sign("Mars") == self.get_planet_sign("Rahu"))

        if mars_aspects_rahu or mars_rahu_sign_aspect:
            curse = CurseRecord(
                curse_type="Snake Curse",
                curse_name="Rahu in 5H aspected by Mars - Naga Curse",
                severity="high",
                houses_involved=[5],
                planets_involved=["Rahu", "Mars"],
                lords_involved=[],
                description=(
                    "Rahu in 5H aspected by Mars creates curse of snake (Naga curse). Indicates "
                    "danger from snakes, poisoning, skin diseases, and loss of children. The native "
                    "or children may face snake bites or related accidents. Fear and anxiety about snakes."
                ),
                remedies=[
                    "Recite Maha Mrityunjaya Mantra",
                    "Worship Shiva as Neelkantha (snake protector)",
                    "Perform Naga Puja and Nag Panchami rituals",
                    "Wear protective talismans",
                    "Avoid killing snakes and harm to reptiles",
                    "Donation to snake rescue organizations",
                    "Mars appeasement rituals"
                ]
            )
            self.add_curse(curse)

    def _check_5l_rahu_ketu_axis_saturn_5h_moon(self) -> None:
        """
        Check: 5L in Rahu–Ketu axis & Saturn in 5H conjoined or aspected by Moon
        
        5L on Rahu-Ketu axis with Saturn in 5H connected with Moon.
        """
        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        five_l_house = self.get_planet_house(five_lord)
        five_l_house_sign = self.get_planet_sign(five_lord)
        rahu_sign = self.get_planet_sign("Rahu")
        ketu_sign = self.get_planet_sign("Ketu")

        # 5L in Rahu-Ketu axis means 5L in same sign as Rahu or Ketu
        five_l_on_axis = (five_l_house_sign == rahu_sign) or (five_l_house_sign == ketu_sign)

        if not five_l_on_axis:
            return

        saturn_in_5h = self.is_planet_in_house("Saturn", 5)
        if not saturn_in_5h:
            return

        # Check Saturn with Moon or Moon aspect
        moon_saturn_together = self.is_planets_together("Saturn", "Moon")
        moon_aspects_saturn = self.is_planet_aspected_by("Saturn", ["Moon"])

        if moon_saturn_together or moon_aspects_saturn:
            curse = CurseRecord(
                curse_type="Snake Curse",
                curse_name="5L on Rahu-Ketu Axis with Saturn in 5H - Severe Naga Curse",
                severity="high",
                houses_involved=[5],
                planets_involved=["Saturn", "Moon", "Rahu", "Ketu", five_lord],
                lords_involved=[five_lord],
                description=(
                    "5L on Rahu-Ketu axis with Saturn in 5H connected to Moon creates severe snake curse. "
                    "Indicates generational curse affecting progeny, recurrent miscarriages or child deaths, "
                    "and chronic illnesses. Danger of snake-related incidents for children."
                ),
                remedies=[
                    "Perform Nag Puja and Nag Panchami rituals annually",
                    "Saturn appeasement (Shani Puja)",
                    "Moon strengthening practices",
                    "Recite Rahu-Ketu mantras",
                    "Charity and service to overcome curse",
                    "Seeking blessings from spiritual masters",
                    "Extreme fasting during Nag Panchami"
                ]
            )
            self.add_curse(curse)

    def _check_jupiter_rahu_5l_weak_ll_mars(self) -> None:
        """
        Check: Jupiter with Rahu, 5L weak, LL & Mars together
        
        Jupiter with Rahu, weak 5L, and Lagna Lord with Mars together creates snake curse.
        """
        jupiter_rahu_together = self.is_planets_together("Jupiter", "Rahu")
        if not jupiter_rahu_together:
            return

        # Check 5L weakness
        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        five_l_debilitated = self.is_planet_debilitated(five_lord)
        five_l_house = self.get_planet_house(five_lord)
        five_l_weak = five_l_debilitated or five_l_house in [6, 8, 12]  # bad house placement

        if not five_l_weak:
            return

        # Get Lagna Lord
        lagna_lord = self.get_nth_lord(1)
        if not lagna_lord:
            return

        # Check Lagna Lord with Mars
        ll_mars_together = self.is_planets_together(lagna_lord, "Mars")
        if not ll_mars_together:
            return

        curse = CurseRecord(
            curse_type="Snake Curse",
            curse_name="Jupiter with Rahu & Weak 5L - Complete Progeny Curse from Snakes",
            severity="high",
            houses_involved=[1, 5],
            planets_involved=["Jupiter", "Rahu", "Mars", five_lord, lagna_lord],
            lords_involved=[five_lord, lagna_lord],
            description=(
                "Jupiter with Rahu, weak 5L, and Lagna Lord with Mars creates the most severe snake curse. "
                "Indicates complete loss of progeny, chronic poisoning or toxicity issues, and recurrent "
                "dangers from snakes or reptiles. Children unable to survive or thrive. Generational curse."
            ),
            remedies=[
                "Perform Maha Mrityunjaya Havan",
                "Nag Puja and appeasement rituals",
                "Jupiter strengthening (Brihaspati Homam)",
                "Rahu and Mars appeasement",
                "Extreme spiritual practices and penance",
                "Seek guidance from enlightened masters",
                "Long-term meditation and mantra practice",
                "Recite Shiva Purana and Nag related texts"
            ]
        )
        self.add_curse(curse)
