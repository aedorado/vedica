"""
Brother Curses Detection Module.

Detects curses from brothers based on specific planetary placements and conjunctions.
Reference: Vedic texts on sibling relationships and karmic afflictions.
"""

import logging
from typing import Dict, List, Optional
from .curse_detector_base import CurseDetectorBase, CurseRecord

logger = logging.getLogger(__name__)


class BrotherCurseDetector(CurseDetectorBase):
    """Detects curses from brothers based on planetary placements."""

    def __init__(self, planet_data_objs: Dict, house_data_objs: Dict):
        """
        Initialize Brother Curse Detector.
        
        Args:
            planet_data_objs: Dictionary of planet objects
            house_data_objs: Dictionary of house objects
        """
        super().__init__(planet_data_objs, house_data_objs)
        self.detected_curses: List[CurseRecord] = []

    def detect_curses(self) -> List[CurseRecord]:
        """Detect all brother curses."""
        logger.info("Detecting Brother Curses...")
        
        self._check_mars_rahu_lagna_3l_5h_8l_8h()
        self._check_debilitated_jupiter_3h_saturn_5h_moon_mars_8h()
        self._check_3l_5h_malefics_rahu_jupiter()
        self._check_10l_malefic_3h_mars_benefic_5h()
        self._check_3l_8h_jupiter_saturn_rahu_5h()
        
        return self.detected_curses

    def _check_mars_rahu_lagna_3l_5h_8l_8h(self) -> None:
        """
        Check: Mars and Rahu in Lagna and 3L in 5H and 8th lord in 8H
        
        Mars and Rahu together in Lagna with 3L in 5H and 8L in 8H creates curse of brother.
        """
        mars_in_1h = self.is_planet_in_house("Mars", 1)
        rahu_in_1h = self.is_planet_in_house("Rahu", 1)
        mars_rahu_together = self.is_planets_together("Mars", "Rahu")
        
        if not (mars_in_1h and rahu_in_1h and mars_rahu_together):
            return

        three_lord = self.get_nth_lord(3)
        eight_lord = self.get_nth_lord(8)
        
        if not (three_lord and eight_lord):
            return

        three_l_in_5h = self.is_planet_in_house(three_lord, 5)
        eight_l_in_8h = self.is_planet_in_house(eight_lord, 8)

        if three_l_in_5h and eight_l_in_8h:
            curse = CurseRecord(
                curse_type="Brother Curse",
                curse_name="Mars & Rahu in Lagna - Sibling Conflict Curse",
                severity="high",
                houses_involved=[1, 3, 5, 8],
                planets_involved=["Mars", "Rahu", three_lord, eight_lord],
                lords_involved=[three_lord, eight_lord],
                description=(
                    "Mars and Rahu conjunction in Lagna with 3L in 5H and 8L in 8H "
                    "creates severe curse of brother. Indicates intense sibling rivalry, "
                    "conflict, and potential physical harm or death of brothers. "
                    "The native may face loss due to brothers' actions."
                ),
                remedies=[
                    "Recite Hanuman Chalisa",
                    "Mars appeasing rituals (Mangal Puja)",
                    "Offer prayers to brothers and family unity",
                    "Worship Kartikeya for sibling harmony",
                    "Perform Rahu shanti rituals"
                ]
            )
            self.add_curse(curse)

    def _check_debilitated_jupiter_3h_saturn_5h_moon_mars_8h(self) -> None:
        """
        Check: Debilitated Jupiter in 3H, Saturn in 5H and Moon, Mars in 8H
        
        Debilitated Jupiter in 3H with Saturn in 5H and Moon, Mars in 8H indicates curse.
        """
        jupiter_debilitated_3h = (
            self.is_planet_debilitated("Jupiter") and 
            self.is_planet_in_house("Jupiter", 3)
        )
        
        if not jupiter_debilitated_3h:
            return

        saturn_in_5h = self.is_planet_in_house("Saturn", 5)
        moon_in_8h = self.is_planet_in_house("Moon", 8)
        mars_in_8h = self.is_planet_in_house("Mars", 8)
        moon_mars_together = self.is_planets_together("Moon", "Mars")

        if saturn_in_5h and moon_in_8h and mars_in_8h and moon_mars_together:
            curse = CurseRecord(
                curse_type="Brother Curse",
                curse_name="Debilitated Jupiter in 3H - Sibling Death Curse",
                severity="high",
                houses_involved=[3, 5, 8],
                planets_involved=["Jupiter", "Saturn", "Moon", "Mars"],
                lords_involved=[],
                description=(
                    "Debilitated Jupiter in 3H with Saturn in 5H and Moon, Mars conjunction "
                    "in 8H creates severe curse of brother leading to loss of sibling. "
                    "Indicates death or severe illness of younger brothers or sisters."
                ),
                remedies=[
                    "Jupiter strengthening rituals (Brihaspati Homam)",
                    "Moon pacifying remedies",
                    "Mars appeasement (Mangal Puja)",
                    "Regular Durga Saptashati recitation",
                    "Support and care for family members"
                ]
            )
            self.add_curse(curse)

    def _check_3l_5h_malefics_rahu_jupiter(self) -> None:
        """
        Check: 3L in 5H and connection of 5th, 8th, 3rd with malefics and Rahu in rashi of Jupiter
        
        3L in 5H with malefics connecting 3rd/5th/8th and Rahu in Jupiter's sign.
        """
        three_lord = self.get_nth_lord(3)
        five_lord = self.get_nth_lord(5)
        eight_lord = self.get_nth_lord(8)

        if not (three_lord and five_lord and eight_lord):
            return

        three_l_in_5h = self.is_planet_in_house(three_lord, 5)
        if not three_l_in_5h:
            return

        # Check if malefics (Mars, Saturn, Rahu) are in 3rd, 5th, or 8th
        malefics = ["Mars", "Saturn", "Rahu", "Sun"]
        malefic_in_3 = any(self.is_planet_in_house(m, 3) for m in malefics)
        malefic_in_5 = any(self.is_planet_in_house(m, 5) for m in malefics)
        malefic_in_8 = any(self.is_planet_in_house(m, 8) for m in malefics)

        # Check if Rahu is in Jupiter's sign
        jupiter_sign = self.get_planet_sign("Jupiter")
        rahu_sign = self.get_planet_sign("Rahu")
        rahu_in_jupiter_sign = jupiter_sign and rahu_sign and jupiter_sign == rahu_sign

        if (malefic_in_3 or malefic_in_5 or malefic_in_8) and rahu_in_jupiter_sign:
            curse = CurseRecord(
                curse_type="Brother Curse",
                curse_name="3L in 5H with Malefics - Sibling Suffering Curse",
                severity="high",
                houses_involved=[3, 5, 8],
                planets_involved=["Mars", "Saturn", "Rahu", three_lord],
                lords_involved=[three_lord, five_lord, eight_lord],
                description=(
                    "3L in 5H with malefic placements in 3rd/5th/8th and Rahu in Jupiter's sign "
                    "creates curse of brother affecting younger siblings. Indicates betrayal, "
                    "separation, or harm coming through brothers."
                ),
                remedies=[
                    "Hanuman Mantra recitation",
                    "Saturn appeasing rituals",
                    "Rahu shanti havan",
                    "Protection of younger siblings",
                    "Maintain sibling harmony"
                ]
            )
            self.add_curse(curse)

    def _check_10l_malefic_3h_mars_benefic_5h(self) -> None:
        """
        Check: 10th lord with malefic placed in 3H and Mars with benefic in 5H
        
        10L with malefic in 3H and Mars with benefic in 5H indicates brother curse.
        """
        ten_lord = self.get_nth_lord(10)
        if not ten_lord:
            return

        # Check 10L with malefic in 3H
        ten_l_in_3h = self.is_planet_in_house(ten_lord, 3)
        if not ten_l_in_3h:
            return

        malefics_in_3 = any(self.is_planet_in_house(m, 3) for m in ["Mars", "Saturn", "Rahu", "Sun"])
        if not malefics_in_3:
            return

        # Check Mars with benefic in 5H
        mars_in_5h = self.is_planet_in_house("Mars", 5)
        if not mars_in_5h:
            return

        benefics_in_5 = any(self.is_planet_in_house(b, 5) for b in ["Jupiter", "Venus", "Moon"])
        mars_with_benefic = mars_in_5h and benefics_in_5

        if mars_with_benefic:
            curse = CurseRecord(
                curse_type="Brother Curse",
                curse_name="10L with Malefic in 3H - Career & Sibling Curse",
                severity="medium",
                houses_involved=[3, 5, 10],
                planets_involved=["Mars", ten_lord],
                lords_involved=[ten_lord],
                description=(
                    "10L with malefic in 3H and Mars with benefic in 5H creates curse affecting "
                    "brother relationships and career through siblings. May cause loss of authority "
                    "or status due to brothers' actions."
                ),
                remedies=[
                    "Career protection rituals",
                    "Mars strengthening practices",
                    "Maintain professional distance from family conflicts",
                    "Regular meditation",
                    "Charitable acts for harmony"
                ]
            )
            self.add_curse(curse)

    def _check_3l_8h_jupiter_saturn_rahu_5h(self) -> None:
        """
        Check: 3L in 8H and Jupiter with Saturn and Rahu in 5H
        
        3L in 8H with Jupiter, Saturn, Rahu conjunction in 5H creates severe brother curse.
        """
        three_lord = self.get_nth_lord(3)
        if not three_lord:
            return

        three_l_in_8h = self.is_planet_in_house(three_lord, 8)
        if not three_l_in_8h:
            return

        # Check Jupiter, Saturn, Rahu in 5H
        jupiter_in_5h = self.is_planet_in_house("Jupiter", 5)
        saturn_in_5h = self.is_planet_in_house("Saturn", 5)
        rahu_in_5h = self.is_planet_in_house("Rahu", 5)

        if jupiter_in_5h and saturn_in_5h and rahu_in_5h:
            curse = CurseRecord(
                curse_type="Brother Curse",
                curse_name="3L in 8H - Triple Malefic in 5H - Severe Sibling Curse",
                severity="high",
                houses_involved=[3, 5, 8],
                planets_involved=["Jupiter", "Saturn", "Rahu", three_lord],
                lords_involved=[three_lord],
                description=(
                    "3L in 8H with Jupiter, Saturn, Rahu conjunction in 5H creates the most severe "
                    "curse of brother. Indicates potential death of brothers, complete estrangement, "
                    "or serious accidents/harm. Past life karmic debt with siblings."
                ),
                remedies=[
                    "Perform Maha Mrityunjaya Havan",
                    "Ancestral puja for siblings",
                    "Extreme fasting and penance",
                    "Seek blessings from elders",
                    "Complete reconciliation with family"
                ]
            )
            self.add_curse(curse)
