"""
Spouse/Wife Curses Detection Module.

Detects curses affecting spouse/wife based on specific planetary placements and conjunctions.
Reference: Vedic texts on marriage and relationship afflictions.
"""

import logging
from typing import Dict, List, Optional
from .curse_detector_base import CurseDetectorBase, CurseRecord

logger = logging.getLogger(__name__)


class SpouseCurseDetector(CurseDetectorBase):
    """Detects curses affecting spouse/wife based on planetary placements."""

    def __init__(self, planet_data_objs: Dict, house_data_objs: Dict):
        """
        Initialize Spouse Curse Detector.
        
        Args:
            planet_data_objs: Dictionary of planet objects
            house_data_objs: Dictionary of house objects
        """
        super().__init__(planet_data_objs, house_data_objs)
        self.detected_curses: List[CurseRecord] = []

    def detect_curses(self) -> List[CurseRecord]:
        """Detect all spouse curses."""
        logger.info("Detecting Spouse Curses...")
        
        self._check_7l_8h_8l_5h_jupiter_malefic()
        self._check_7l_8h_venus_5h_jupiter_malefics()
        self._check_7l_8h_malefics_lagna_2h_5h()
        self._check_saturn_venus_7h_8l_5h_sun_rahu_lagna()
        self._check_5h_venus_rahu_saturn_mars_2h_jupiter_12h()
        self._check_rahu_lagna_saturn_5h_mars_9h()
        
        return self.detected_curses

    def _check_7l_8h_8l_5h_jupiter_malefic(self) -> None:
        """
        Check: 7L in 8H, 8L in 5H and connection of Jupiter as functional malefic
        
        7L in 8H with 8L in 5H and Jupiter acting as functional malefic.
        """
        seven_lord = self.get_nth_lord(7)
        eight_lord = self.get_nth_lord(8)

        if not (seven_lord and eight_lord):
            return

        seven_l_in_8h = self.is_planet_in_house(seven_lord, 8)
        eight_l_in_5h = self.is_planet_in_house(eight_lord, 5)

        if not (seven_l_in_8h and eight_l_in_5h):
            return

        # Check if Jupiter is with malefics (functional malefic)
        jupiter_with_malefics = any(
            self.is_planets_together("Jupiter", m) for m in ["Mars", "Saturn", "Rahu", "Sun"]
        )

        if jupiter_with_malefics:
            curse = CurseRecord(
                curse_type="Spouse Curse",
                curse_name="7L in 8H & 8L in 5H - Spouse Death Curse",
                severity="high",
                houses_involved=[5, 7, 8],
                planets_involved=["Jupiter", "Mars", "Saturn", "Rahu", seven_lord, eight_lord],
                lords_involved=[seven_lord, eight_lord],
                description=(
                    "7L in 8H with 8L in 5H and Jupiter as functional malefic creates severe curse "
                    "of spouse. Indicates loss of spouse through death, divorce, or severe illness. "
                    "The marriage suffers from misfortune and separation."
                ),
                remedies=[
                    "Perform Sudarshan Chakra Puja",
                    "Venus strengthening rituals",
                    "Mars and Saturn appeasement",
                    "Jupiter purification practices",
                    "Marriage protection rituals",
                    "Worship Parvati-Mahakal for marital bliss"
                ]
            )
            self.add_curse(curse)

    def _check_7l_8h_venus_5h_jupiter_malefics(self) -> None:
        """
        Check: 7L in 8H, Venus in 5H and Jupiter with malefics
        
        7L in 8H with Venus in 5H and Jupiter conjunction with malefics.
        """
        seven_lord = self.get_nth_lord(7)
        if not seven_lord:
            return

        seven_l_in_8h = self.is_planet_in_house(seven_lord, 8)
        venus_in_5h = self.is_planet_in_house("Venus", 5)

        if not (seven_l_in_8h and venus_in_5h):
            return

        # Check Jupiter with malefics
        jupiter_with_malefics = any(
            self.is_planets_together("Jupiter", m) for m in ["Mars", "Saturn", "Rahu"]
        )

        if jupiter_with_malefics:
            curse = CurseRecord(
                curse_type="Spouse Curse",
                curse_name="7L in 8H with Venus in 5H - Marital Suffering Curse",
                severity="high",
                houses_involved=[5, 7, 8],
                planets_involved=["Venus", "Jupiter", "Mars", "Saturn", "Rahu", seven_lord],
                lords_involved=[seven_lord],
                description=(
                    "7L in 8H with Venus in 5H and Jupiter with malefics creates curse of spouse. "
                    "Indicates marital conflict, infidelity, health problems of spouse, and potential "
                    "widowhood. Lack of marital happiness and conjugal rights."
                ),
                remedies=[
                    "Venus strengthening practices (wearing diamonds)",
                    "Perform Lakshmi-Narayana Puja",
                    "Fast on Fridays",
                    "Chant Venus mantras",
                    "Marriage counseling and harmony practices",
                    "Donate to widow shelters"
                ]
            )
            self.add_curse(curse)

    def _check_7l_8h_malefics_lagna_2h_5h(self) -> None:
        """
        Check: 7L in 8H, malefics in Lagna, 2H and 5H
        
        7L in 8H with malefic placements in Lagna, 2H, and 5H.
        """
        seven_lord = self.get_nth_lord(7)
        if not seven_lord:
            return

        seven_l_in_8h = self.is_planet_in_house(seven_lord, 8)
        if not seven_l_in_8h:
            return

        # Check malefics in Lagna, 2H, 5H
        malefics = ["Mars", "Saturn", "Rahu", "Sun", "Mercury"]
        malefic_in_1 = any(self.is_planet_in_house(m, 1) for m in malefics)
        malefic_in_2 = any(self.is_planet_in_house(m, 2) for m in malefics)
        malefic_in_5 = any(self.is_planet_in_house(m, 5) for m in malefics)

        if malefic_in_1 and malefic_in_2 and malefic_in_5:
            curse = CurseRecord(
                curse_type="Spouse Curse",
                curse_name="7L in 8H with Triple Malefic Placement - Severe Marital Curse",
                severity="high",
                houses_involved=[1, 2, 5, 7, 8],
                planets_involved=["Mars", "Saturn", "Rahu", "Sun", seven_lord],
                lords_involved=[seven_lord],
                description=(
                    "7L in 8H with malefics distributed in Lagna, 2H, and 5H creates severe curse "
                    "of spouse. Indicates complete marital breakdown, loss of spouse through death or "
                    "abandonment, and children-related suffering. Financial losses due to spouse."
                ),
                remedies=[
                    "Perform Navagraha Shanti Havan",
                    "Mars, Saturn, and Rahu appeasement",
                    "Maha Mrityunjaya Mantra for spouse protection",
                    "Daily Durga Saptashati recitation",
                    "Marriage renewal ceremonies",
                    "Extreme fasting and penance for marital harmony"
                ]
            )
            self.add_curse(curse)

    def _check_saturn_venus_7h_8l_5h_sun_rahu_lagna(self) -> None:
        """
        Check: Saturn and Venus in 7H and 8L in 5H, Sun in Lagna with Rahu
        
        Saturn and Venus in 7H with 8L in 5H and Sun with Rahu in Lagna.
        """
        saturn_in_7h = self.is_planet_in_house("Saturn", 7)
        venus_in_7h = self.is_planet_in_house("Venus", 7)
        saturn_venus_together = self.is_planets_together("Saturn", "Venus")

        if not (saturn_in_7h and venus_in_7h and saturn_venus_together):
            return

        eight_lord = self.get_nth_lord(8)
        if not eight_lord:
            return

        eight_l_in_5h = self.is_planet_in_house(eight_lord, 5)
        sun_in_1h = self.is_planet_in_house("Sun", 1)
        rahu_in_1h = self.is_planet_in_house("Rahu", 1)
        sun_rahu_together = self.is_planets_together("Sun", "Rahu")

        if eight_l_in_5h and sun_in_1h and rahu_in_1h and sun_rahu_together:
            curse = CurseRecord(
                curse_type="Spouse Curse",
                curse_name="Saturn-Venus in 7H with 8L in 5H - Widowhood/Divorce Curse",
                severity="high",
                houses_involved=[1, 5, 7, 8],
                planets_involved=["Saturn", "Venus", "Sun", "Rahu", eight_lord],
                lords_involved=[eight_lord],
                description=(
                    "Saturn and Venus conjunction in 7H with 8L in 5H and Sun-Rahu in Lagna creates "
                    "severe curse of spouse leading to widowhood or divorce. Indicates early death of "
                    "spouse, or chronic marital separation. Children may suffer loss of parent."
                ),
                remedies=[
                    "Saturn and Venus appeasement rituals",
                    "Perform Sade Sati management practices",
                    "Sun strengthening practices",
                    "Rahu shanti havan",
                    "Widow protection and support",
                    "Remarriage post-widowhood if needed"
                ]
            )
            self.add_curse(curse)

    def _check_5h_venus_rahu_saturn_mars_2h_jupiter_12h(self) -> None:
        """
        Check: 5H with Venus/Rahu/Saturn or aspected by them, Mars in 2H, Jupiter in 12H
        
        5H containing or aspected by Venus, Rahu, Saturn with Mars in 2H and Jupiter in 12H.
        """
        # Check 5H planets
        venus_in_5h = self.is_planet_in_house("Venus", 5)
        rahu_in_5h = self.is_planet_in_house("Rahu", 5)
        saturn_in_5h = self.is_planet_in_house("Saturn", 5)

        five_h_afflicted = venus_in_5h or rahu_in_5h or saturn_in_5h

        if not five_h_afflicted:
            return

        # Check Mars in 2H and Jupiter in 12H
        mars_in_2h = self.is_planet_in_house("Mars", 2)
        jupiter_in_12h = self.is_planet_in_house("Jupiter", 12)

        if mars_in_2h and jupiter_in_12h:
            curse = CurseRecord(
                curse_type="Spouse Curse",
                curse_name="5H Afflicted with Mars in 2H - Children & Spouse Curse",
                severity="high",
                houses_involved=[2, 5, 12],
                planets_involved=["Venus", "Rahu", "Saturn", "Mars", "Jupiter"],
                lords_involved=[],
                description=(
                    "5H afflicted by Venus, Rahu, or Saturn with Mars in 2H and Jupiter in 12H "
                    "creates curse affecting both spouse and children. Indicates loss of children, "
                    "marital discord, and financial losses through family. Separation from spouse."
                ),
                remedies=[
                    "Venus strengthening rituals",
                    "Jupiter remedies (wearing topaz)",
                    "Mars appeasement",
                    "Rahu shanti if Rahu in 5H",
                    "5th house purification ceremonies",
                    "Children protection rituals"
                ]
            )
            self.add_curse(curse)

    def _check_rahu_lagna_saturn_5h_mars_9h(self) -> None:
        """
        Check: Rahu in Lagna, Saturn in 5H and Mars in 9H along with 5L and 7L in 8H
        
        Rahu in Lagna with Saturn in 5H, Mars in 9H, and 5L, 7L both in 8H.
        """
        rahu_in_1h = self.is_planet_in_house("Rahu", 1)
        saturn_in_5h = self.is_planet_in_house("Saturn", 5)
        mars_in_9h = self.is_planet_in_house("Mars", 9)

        if not (rahu_in_1h and saturn_in_5h and mars_in_9h):
            return

        five_lord = self.get_nth_lord(5)
        seven_lord = self.get_nth_lord(7)

        if not (five_lord and seven_lord):
            return

        five_l_in_8h = self.is_planet_in_house(five_lord, 8)
        seven_l_in_8h = self.is_planet_in_house(seven_lord, 8)

        if five_l_in_8h and seven_l_in_8h:
            curse = CurseRecord(
                curse_type="Spouse Curse",
                curse_name="Rahu-Saturn-Mars Configuration - Complete Marital Curse",
                severity="high",
                houses_involved=[1, 5, 7, 8, 9],
                planets_involved=["Rahu", "Saturn", "Mars", five_lord, seven_lord],
                lords_involved=[five_lord, seven_lord],
                description=(
                    "Rahu in Lagna with Saturn in 5H, Mars in 9H, and both 5L and 7L in 8H creates "
                    "the most severe curse affecting marriage and progeny. Indicates certain widowhood, "
                    "loss of children, and complete marital failure. Karmic debts from past life."
                ),
                remedies=[
                    "Perform Maha Mrityunjaya Havan",
                    "Extreme penance and fasting",
                    "Rahu, Saturn, and Mars appeasement",
                    "Seek ashram stay and spiritual practices",
                    "Complete life transformation",
                    "Worship Durga and Shiva for divine protection"
                ]
            )
            self.add_curse(curse)
