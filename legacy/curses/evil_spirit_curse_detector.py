"""
Evil Spirit Curses Detection Module.

Detects curses from evil spirits, demons, and negative entities based on planetary placements.
Reference: Vedic texts on Bhuta (evil spirit) and Daemonic afflictions.
"""

import logging
from typing import Dict, List, Optional
from .curse_detector_base import CurseDetectorBase, CurseRecord

logger = logging.getLogger(__name__)


class EvilSpiritCurseDetector(CurseDetectorBase):
    """Detects curses from evil spirits based on planetary placements."""

    def __init__(self, planet_data_objs: Dict, house_data_objs: Dict):
        """
        Initialize Evil Spirit Curse Detector.
        
        Args:
            planet_data_objs: Dictionary of planet objects
            house_data_objs: Dictionary of house objects
        """
        super().__init__(planet_data_objs, house_data_objs)
        self.detected_curses: List[CurseRecord] = []

    def detect_curses(self) -> List[CurseRecord]:
        """Detect all evil spirit curses."""
        logger.info("Detecting Evil Spirit Curses...")
        
        self._check_saturn_sun_5h_weak_moon_7h_rahu_jupiter_12h()
        self._check_saturn_5l_8h_mars_lagna_jupiter_8h()
        self._check_rahu_lagna_saturn_5h_jupiter_6_8h()
        self._check_jupiter_5l_debilitated_aspected_debilitated()
        self._check_saturn_lagna_rahu_5h_sun_mars_12h()
        self._check_saturn_venus_8l_5h_jupiter_8h()
        
        return self.detected_curses

    def _check_saturn_sun_5h_weak_moon_7h_rahu_jupiter_12h(self) -> None:
        """
        Check: Saturn and Sun in 5H, weak Moon in 7H, Rahu in Lagna, Jupiter in 12H
        
        Complex multiple planetary configuration indicating evil spirit possession.
        """
        saturn_in_5h = self.is_planet_in_house("Saturn", 5)
        sun_in_5h = self.is_planet_in_house("Sun", 5)
        moon_in_7h = self.is_planet_in_house("Moon", 7)
        moon_debilitated = self.is_planet_debilitated("Moon")
        rahu_in_1h = self.is_planet_in_house("Rahu", 1)
        jupiter_in_12h = self.is_planet_in_house("Jupiter", 12)

        if (saturn_in_5h and sun_in_5h and moon_in_7h and moon_debilitated and 
            rahu_in_1h and jupiter_in_12h):
            curse = CurseRecord(
                curse_type="Evil Spirit Curse",
                curse_name="Multi-Planetary Evil Spirit Configuration",
                severity="high",
                houses_involved=[1, 5, 7, 12],
                planets_involved=["Saturn", "Sun", "Moon", "Rahu", "Jupiter"],
                lords_involved=[],
                description=(
                    "Saturn and Sun in 5H with weak Moon in 7H, Rahu in Lagna, and Jupiter in 12H creates curse "
                    "of direct evil spirit or demon possession. Indicates obsession by negative entities, extreme "
                    "mental afflictions, psychological disturbances, and supernatural haunting."
                ),
                remedies=[
                    "Perform Maha Mrityunjaya Havan urgently",
                    "Evil spirit appeasement rituals",
                    "Saturn, Sun, and Rahu shanti practices",
                    "Jupiter strengthening (Brihaspati Homam)",
                    "Protective mantras and talismans",
                    "Immediate spiritual healing and exorcism"
                ]
            )
            self.add_curse(curse)

    def _check_saturn_5l_8h_mars_lagna_jupiter_8h(self) -> None:
        """
        Check: Saturn as 5L in 8H, Mars in Lagna, Jupiter in 8H
        
        Saturn 5L in 8H with Mars Lagna and Jupiter in 8H.
        """
        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        saturn_5l_in_8h = (five_lord == "Saturn" and self.is_planet_in_house("Saturn", 8))
        if not saturn_5l_in_8h:
            return

        mars_in_1h = self.is_planet_in_house("Mars", 1)
        jupiter_in_8h = self.is_planet_in_house("Jupiter", 8)

        if mars_in_1h and jupiter_in_8h:
            curse = CurseRecord(
                curse_type="Evil Spirit Curse",
                curse_name="Saturn 5L in 8H - Evil Spirit Attraction",
                severity="high",
                houses_involved=[1, 5, 8],
                planets_involved=["Saturn", "Mars", "Jupiter"],
                lords_involved=[five_lord],
                description=(
                    "Saturn as 5L in 8H with Mars in Lagna and Jupiter in 8H creates curse attracting evil spirits. "
                    "Indicates attraction to negative astral entities, occult bondage, loss of progeny, and "
                    "supernatural afflictions affecting the household."
                ),
                remedies=[
                    "Perform Maha Mrityunjaya Havan",
                    "Saturn appeasement (Shani Puja)",
                    "Mars protection rituals",
                    "Jupiter strengthening",
                    "Protective mantras and yantras",
                    "Exorcism and spiritual cleansing rituals"
                ]
            )
            self.add_curse(curse)

    def _check_rahu_lagna_saturn_5h_jupiter_6_8h(self) -> None:
        """
        Check: Rahu in Lagna, Saturn in 5H, Jupiter in 6H or 8H
        
        Rahu in Lagna with Saturn in 5H and Jupiter afflicted.
        """
        rahu_in_1h = self.is_planet_in_house("Rahu", 1)
        if not rahu_in_1h:
            return

        saturn_in_5h = self.is_planet_in_house("Saturn", 5)
        if not saturn_in_5h:
            return

        jupiter_in_6h = self.is_planet_in_house("Jupiter", 6)
        jupiter_in_8h = self.is_planet_in_house("Jupiter", 8)

        if jupiter_in_6h or jupiter_in_8h:
            curse = CurseRecord(
                curse_type="Evil Spirit Curse",
                curse_name="Rahu-Saturn Configuration - Demonic Influence",
                severity="high",
                houses_involved=[1, 5, 6, 8],
                planets_involved=["Rahu", "Saturn", "Jupiter"],
                lords_involved=[],
                description=(
                    "Rahu in Lagna with Saturn in 5H and Jupiter in 6H/8H creates curse of demonic influence. "
                    "Indicates vulnerability to negative entities, dark occult attractions, loss of children, "
                    "and constant supernatural disturbances."
                ),
                remedies=[
                    "Rahu shanti rituals urgently",
                    "Saturn appeasement (Shani Puja)",
                    "Jupiter strengthening (Brihaspati Homam)",
                    "Evil spirit appeasement ceremonies",
                    "Protective mantras daily",
                    "Seek exorcism from spiritual masters"
                ]
            )
            self.add_curse(curse)

    def _check_jupiter_5l_debilitated_aspected_debilitated(self) -> None:
        """
        Check: Jupiter and 5L debilitated, aspected by another debilitated planet
        
        Multiple debilitated planets in configuration.
        """
        jupiter_debilitated = self.is_planet_debilitated("Jupiter")
        if not jupiter_debilitated:
            return

        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        five_l_debilitated = self.is_planet_debilitated(five_lord)
        if not five_l_debilitated:
            return

        # Find other debilitated planets
        debilitated_planets = []
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Venus", "Saturn"]:
            if planet != "Jupiter" and planet != five_lord:
                if self.is_planet_debilitated(planet):
                    debilitated_planets.append(planet)

        # Check if any debilitated planet aspects Jupiter or 5L
        for deb_planet in debilitated_planets:
            if (self.is_planet_aspected_by("Jupiter", [deb_planet]) or 
                self.is_planet_aspected_by(five_lord, [deb_planet])):
                curse = CurseRecord(
                    curse_type="Evil Spirit Curse",
                    curse_name="Multiple Debilitated Planets - Supernatural Weakness",
                    severity="high",
                    houses_involved=[5],
                    planets_involved=["Jupiter", five_lord, deb_planet],
                    lords_involved=[five_lord],
                    description=(
                        "Jupiter and 5L debilitated with aspect from another debilitated planet creates curse "
                        "of spiritual weakness. Indicates extreme vulnerability to evil spirits, supernatural "
                        "afflictions, loss of progeny, and inability to resist negative influences."
                    ),
                    remedies=[
                        "Perform Navagraha Shanti Havan",
                        "Jupiter strengthening (Brihaspati Homam)",
                        "All debilitated planet appeasement",
                        "Spiritual protection rituals",
                        "Daily protective mantras",
                        "Seek spiritual master's guidance"
                    ]
                )
                self.add_curse(curse)
                return

    def _check_saturn_lagna_rahu_5h_sun_mars_12h(self) -> None:
        """
        Check: Saturn in Lagna, Rahu in 5H, Sun in 5H, Mars in 12H
        
        Saturn Lagna with multiple malefics in 5H and 12H.
        """
        saturn_in_1h = self.is_planet_in_house("Saturn", 1)
        if not saturn_in_1h:
            return

        rahu_in_5h = self.is_planet_in_house("Rahu", 5)
        sun_in_5h = self.is_planet_in_house("Sun", 5)
        mars_in_12h = self.is_planet_in_house("Mars", 12)

        if rahu_in_5h and sun_in_5h and mars_in_12h:
            curse = CurseRecord(
                curse_type="Evil Spirit Curse",
                curse_name="Saturn Lagna with Triple Malefic - Complete Spirit Possession",
                severity="high",
                houses_involved=[1, 5, 12],
                planets_involved=["Saturn", "Rahu", "Sun", "Mars"],
                lords_involved=[],
                description=(
                    "Saturn in Lagna with Rahu and Sun in 5H and Mars in 12H creates curse of complete spirit "
                    "possession. Indicates direct occupancy by evil spirits, severe mental and physical torment, "
                    "loss of all children, and complete life destruction."
                ),
                remedies=[
                    "Immediate Maha Mrityunjaya Havan",
                    "Saturn appeasement urgently",
                    "Rahu shanti rituals",
                    "Sun and Mars protection ceremonies",
                    "Evil spirit appeasement rituals",
                    "Immediate exorcism and spiritual healing"
                ]
            )
            self.add_curse(curse)

    def _check_saturn_venus_8l_5h_jupiter_8h(self) -> None:
        """
        Check: Saturn, Venus, 8L in 5H with Jupiter in 8H
        
        Multiple malefics in 5H with Jupiter in 8H.
        """
        saturn_in_5h = self.is_planet_in_house("Saturn", 5)
        venus_in_5h = self.is_planet_in_house("Venus", 5)
        jupiter_in_8h = self.is_planet_in_house("Jupiter", 8)

        if not (saturn_in_5h and venus_in_5h and jupiter_in_8h):
            return

        eight_lord = self.get_nth_lord(8)
        if not eight_lord:
            return

        eight_l_in_5h = self.is_planet_in_house(eight_lord, 5)

        if eight_l_in_5h:
            curse = CurseRecord(
                curse_type="Evil Spirit Curse",
                curse_name="Saturn-Venus-8L in 5H - Occult Curse Manifestation",
                severity="high",
                houses_involved=[5, 8],
                planets_involved=["Saturn", "Venus", eight_lord, "Jupiter"],
                lords_involved=[eight_lord],
                description=(
                    "Saturn, Venus, and 8L in 5H with Jupiter in 8H creates curse from hidden occult forces. "
                    "Indicates manifestation of ancient curses, black magic effects, loss of progeny, and "
                    "supernatural torment from negative ancestral or enemy spirits."
                ),
                remedies=[
                    "Perform Maha Mrityunjaya Havan",
                    "8th house liberation rituals",
                    "Saturn and Venus appeasement",
                    "Jupiter strengthening (Brihaspati Homam)",
                    "Black magic reversal rituals",
                    "Seek spiritual master for protection"
                ]
            )
            self.add_curse(curse)
