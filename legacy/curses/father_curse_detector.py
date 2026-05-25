"""
Father Curses Detection Module.

Detects curses affecting father based on specific planetary placements and conjunctions.
Reference: Vedic texts on father-child relationships and paternal afflictions.
"""

import logging
from typing import Dict, List, Optional
from .curse_detector_base import CurseDetectorBase, CurseRecord

logger = logging.getLogger(__name__)


class FatherCurseDetector(CurseDetectorBase):
    """Detects curses affecting father based on planetary placements."""

    def __init__(self, planet_data_objs: Dict, house_data_objs: Dict):
        """
        Initialize Father Curse Detector.
        
        Args:
            planet_data_objs: Dictionary of planet objects
            house_data_objs: Dictionary of house objects
        """
        super().__init__(planet_data_objs, house_data_objs)
        self.detected_curses: List[CurseRecord] = []

    def detect_curses(self) -> List[CurseRecord]:
        """Detect all father curses."""
        logger.info("Detecting Father Curses...")
        
        self._check_sun_saturn_mars_lagna_5h_rahu_jupiter_8h_12h()
        self._check_lagna_lord_5l_malefics_10l_jupiter_bad()
        self._check_sun_8h_saturn_5h_5l_rahu_lagna_lord_malefic()
        self._check_6l_5h_10l_6h_jupiter_rahu()
        self._check_mars_10l_cancer_aquarius_lagna()
        
        return self.detected_curses

    def _check_sun_saturn_mars_lagna_5h_rahu_jupiter_8h_12h(self) -> None:
        """
        Check: Sun/Saturn/Mars in Lagna & 5H, Rahu & Jupiter in 8H & 12H
        
        Sun, Saturn, or Mars in Lagna and 5H with Rahu and Jupiter in 8H and 12H.
        """
        # Check Sun/Saturn/Mars in Lagna
        malefic_in_1h = any(self.is_planet_in_house(m, 1) for m in ["Sun", "Saturn", "Mars"])
        
        # Check Sun/Saturn/Mars in 5H
        malefic_in_5h = any(self.is_planet_in_house(m, 5) for m in ["Sun", "Saturn", "Mars"])
        
        if not (malefic_in_1h and malefic_in_5h):
            return

        # Check Rahu and Jupiter placement
        rahu_in_8h = self.is_planet_in_house("Rahu", 8)
        rahu_in_12h = self.is_planet_in_house("Rahu", 12)
        jupiter_in_8h = self.is_planet_in_house("Jupiter", 8)
        jupiter_in_12h = self.is_planet_in_house("Jupiter", 12)

        if (rahu_in_8h or rahu_in_12h) and (jupiter_in_8h or jupiter_in_12h):
            curse = CurseRecord(
                curse_type="Father Curse",
                curse_name="Malefics in Lagna-5H with Rahu-Jupiter in 8H-12H",
                severity="high",
                houses_involved=[1, 5, 8, 12],
                planets_involved=["Sun", "Saturn", "Mars", "Rahu", "Jupiter"],
                lords_involved=[],
                description=(
                    "Sun, Saturn, or Mars in Lagna and 5H with Rahu and Jupiter in 8H and 12H "
                    "creates severe curse affecting father. Indicates father's early death, chronic illness, "
                    "or complete separation. Loss of paternal support and guidance."
                ),
                remedies=[
                    "Perform Pitru Shanti (ancestral appeasement)",
                    "Sun strengthening rituals (Surya Namaskar)",
                    "Saturn appeasement (Shani Puja)",
                    "Mars appeasement (Mangal Puja)",
                    "Regular father worship and respect",
                    "Charity to father-figures and elders"
                ]
            )
            self.add_curse(curse)

    def _check_lagna_lord_5l_malefics_10l_jupiter_bad(self) -> None:
        """
        Check: Lagna lord & 5L with malefics, 10L and Jupiter ill placed (6/8/12H)
        
        Lagna lord and 5L conjunction with malefics, 10L and Jupiter in 6/8/12H.
        """
        lagna_lord = self.get_nth_lord(1)
        five_lord = self.get_nth_lord(5)
        ten_lord = self.get_nth_lord(10)

        if not (lagna_lord and five_lord and ten_lord):
            return

        # Check Lagna lord and 5L with malefics
        ll_5l_together = self.is_planets_together(lagna_lord, five_lord)
        if not ll_5l_together:
            return

        malefics_with_ll_5l = any(
            self.is_planets_together(lagna_lord, m) or self.is_planets_together(five_lord, m)
            for m in ["Mars", "Saturn", "Rahu", "Sun"]
        )

        if not malefics_with_ll_5l:
            return

        # Check 10L and Jupiter in bad houses
        bad_houses = [6, 8, 12]
        ten_l_bad = any(self.is_planet_in_house(ten_lord, h) for h in bad_houses)
        jupiter_bad = any(self.is_planet_in_house("Jupiter", h) for h in bad_houses)

        if ten_l_bad and jupiter_bad:
            curse = CurseRecord(
                curse_type="Father Curse",
                curse_name="Lagna-5L with Malefics & Ill-Placed 10L-Jupiter",
                severity="high",
                houses_involved=[1, 5, 6, 8, 10, 12],
                planets_involved=[lagna_lord, five_lord, ten_lord, "Jupiter", "Mars", "Saturn", "Rahu"],
                lords_involved=[lagna_lord, five_lord, ten_lord],
                description=(
                    "Lagna lord and 5L with malefics, combined with 10L and Jupiter in 6/8/12H creates "
                    "severe father curse affecting career, paternal health, and authority loss. Father may "
                    "lose status, wealth, or health. Native loses career guidance from father."
                ),
                remedies=[
                    "Jupiter strengthening (Brihaspati Homam)",
                    "10th house remedies and career rituals",
                    "Father protection and respect practices",
                    "Mars and Saturn appeasement",
                    "Regular temple visits",
                    "Charity for father's well-being"
                ]
            )
            self.add_curse(curse)

    def _check_sun_8h_saturn_5h_5l_rahu_lagna_lord_malefic(self) -> None:
        """
        Check: Sun in 8H, Saturn in 5H, 5L with Rahu, Lagna lord with malefic
        
        Sun in 8H with Saturn in 5H, 5L with Rahu, and Lagna lord with malefic.
        """
        sun_in_8h = self.is_planet_in_house("Sun", 8)
        saturn_in_5h = self.is_planet_in_house("Saturn", 5)

        if not (sun_in_8h and saturn_in_5h):
            return

        five_lord = self.get_nth_lord(5)
        lagna_lord = self.get_nth_lord(1)

        if not (five_lord and lagna_lord):
            return

        # Check 5L with Rahu
        five_l_rahu_together = self.is_planets_together(five_lord, "Rahu")

        # Check Lagna lord with malefic
        ll_malefic = any(
            self.is_planets_together(lagna_lord, m) for m in ["Mars", "Saturn", "Sun", "Rahu"]
        )

        if five_l_rahu_together and ll_malefic:
            curse = CurseRecord(
                curse_type="Father Curse",
                curse_name="Sun in 8H - Father Death & Health Curse",
                severity="high",
                houses_involved=[1, 5, 8],
                planets_involved=["Sun", "Saturn", "Rahu", five_lord, lagna_lord],
                lords_involved=[five_lord, lagna_lord],
                description=(
                    "Sun in 8H with Saturn in 5H, 5L with Rahu, and Lagna lord with malefic creates "
                    "severe curse indicating father's death or critical illness. Sudden loss of father, "
                    "loss of paternal inheritance, and life transformation."
                ),
                remedies=[
                    "Perform Maha Mrityunjaya Havan for father",
                    "Sun worship and Surya Namaskar",
                    "Saturn appeasing rituals",
                    "Rahu shanti practices",
                    "Ancestor worship and Pitru Puja",
                    "Daily father remembrance and prayers"
                ]
            )
            self.add_curse(curse)

    def _check_6l_5h_10l_6h_jupiter_rahu(self) -> None:
        """
        Check: 6L in 5H, 10L in 6H, Jupiter with Rahu
        
        6L in 5H with 10L in 6H and Jupiter with Rahu.
        """
        six_lord = self.get_nth_lord(6)
        ten_lord = self.get_nth_lord(10)

        if not (six_lord and ten_lord):
            return

        six_l_in_5h = self.is_planet_in_house(six_lord, 5)
        ten_l_in_6h = self.is_planet_in_house(ten_lord, 6)

        if not (six_l_in_5h and ten_l_in_6h):
            return

        # Check Jupiter with Rahu
        jupiter_rahu_together = self.is_planets_together("Jupiter", "Rahu")

        if jupiter_rahu_together:
            curse = CurseRecord(
                curse_type="Father Curse",
                curse_name="6L-10L Misplacement with Jupiter-Rahu - Career & Father Loss",
                severity="medium",
                houses_involved=[5, 6, 10],
                planets_involved=[six_lord, ten_lord, "Jupiter", "Rahu"],
                lords_involved=[six_lord, ten_lord],
                description=(
                    "6L in 5H with 10L in 6H and Jupiter with Rahu creates curse affecting father and "
                    "career. Father may face legal issues, disputes, or health problems. Native loses "
                    "career support from father and faces obstacles in professional growth."
                ),
                remedies=[
                    "Jupiter strengthening",
                    "Rahu appeasement rituals",
                    "Career remedies for 10th house",
                    "Enemy/dispute resolution practices",
                    "Father support and cooperation",
                    "Legal protection practices if needed"
                ]
            )
            self.add_curse(curse)

    def _check_mars_10l_cancer_aquarius_lagna(self) -> None:
        """
        Check: Mars as 10L (Cancer/Aquarius Lagna) with 5L & Lagna, 5H and 10H have malefics
        
        Mars as 10L in Cancer/Aquarius Lagna with 5L in Lagna, malefics in 5H and 10H.
        """
        lagna_sign = self.get_lagna_sign()
        
        # Mars is 10L for Cancer and Aquarius Lagna
        mars_is_10l = lagna_sign in ["Cancer", "Aquarius"]
        
        if not mars_is_10l:
            return

        mars_in_lagna = self.is_planet_in_house("Mars", 1)
        if not mars_in_lagna:
            return

        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        five_l_in_1h = self.is_planet_in_house(five_lord, 1)
        if not five_l_in_1h:
            return

        # Check malefics in 5H and 10H
        malefics = ["Mars", "Saturn", "Rahu", "Sun"]
        malefic_in_5h = any(self.is_planet_in_house(m, 5) for m in malefics)
        malefic_in_10h = any(self.is_planet_in_house(m, 10) for m in malefics)

        if malefic_in_5h and malefic_in_10h:
            curse = CurseRecord(
                curse_type="Father Curse",
                curse_name="Mars 10L in Lagna - Severe Career & Father Curse",
                severity="high",
                houses_involved=[1, 5, 10],
                planets_involved=["Mars", five_lord],
                lords_involved=[five_lord],
                description=(
                    "Mars as 10L in Cancer/Aquarius Lagna with 5L in Lagna and malefics in 5H and 10H "
                    "creates severe curse affecting father and career destruction. Indicates father's "
                    "misfortune, career loss for native, and family instability. Complete authority collapse."
                ),
                remedies=[
                    "Mars appeasement (Mangal Puja)",
                    "10th house remedies (career rituals)",
                    "Father blessing and respect",
                    "Saturn and Rahu appeasement if present",
                    "Perform Durga Saptashati",
                    "Extreme fasting and penance for career restoration"
                ]
            )
            self.add_curse(curse)
