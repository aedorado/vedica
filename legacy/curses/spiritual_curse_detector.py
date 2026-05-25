"""
Saint / Spiritual Person Curses Detection Module.

Detects curses affecting spiritual seekers and saints based on planetary placements.
Reference: Vedic texts on spiritual impediments and karmic obstacles.
"""

import logging
from typing import Dict, List, Optional
from .curse_detector_base import CurseDetectorBase, CurseRecord

logger = logging.getLogger(__name__)


class SpiritualCurseDetector(CurseDetectorBase):
    """Detects curses affecting spiritual persons based on planetary placements."""

    def __init__(self, planet_data_objs: Dict, house_data_objs: Dict):
        """
        Initialize Spiritual Curse Detector.
        
        Args:
            planet_data_objs: Dictionary of planet objects
            house_data_objs: Dictionary of house objects
        """
        super().__init__(planet_data_objs, house_data_objs)
        self.detected_curses: List[CurseRecord] = []

    def detect_curses(self) -> List[CurseRecord]:
        """Detect all spiritual curses."""
        logger.info("Detecting Spiritual Person Curses...")
        
        self._check_rahu_jupiter_sign_malefics_5_8_9h()
        self._check_9l_5h_jupiter_rahu_mars_8h()
        self._check_9l_debilitated_12l_5h_rahu()
        self._check_jupiter_debilitated_rahu_5h_5l_trikona()
        self._check_jupiter_5l_8h_sun_moon()
        self._check_jupiter_saturn_navamsha_with_malefics_5l_12h()
        self._check_jupiter_saturn_lagna_rahu_9h_or_12h()
        
        return self.detected_curses

    def _check_rahu_jupiter_sign_malefics_5_8_9h(self) -> None:
        """
        Check: Rahu in rashi of Jupiter, connection of Jupiter, Saturn, Mars with 5H, 8H, 9H
        
        Rahu in Jupiter's sign with Jupiter, Saturn, Mars in 5H, 8H, or 9H.
        """
        jupiter_sign = self.get_planet_sign("Jupiter")
        rahu_sign = self.get_planet_sign("Rahu")

        if not (jupiter_sign and rahu_sign and jupiter_sign == rahu_sign):
            return

        # Check connections of Jupiter, Saturn, Mars with 5H, 8H, 9H
        key_houses = [5, 8, 9]
        jupiter_connected = any(self.is_planet_in_house("Jupiter", h) for h in key_houses)
        saturn_connected = any(self.is_planet_in_house("Saturn", h) for h in key_houses)
        mars_connected = any(self.is_planet_in_house("Mars", h) for h in key_houses)

        if jupiter_connected and saturn_connected and mars_connected:
            curse = CurseRecord(
                curse_type="Spiritual Curse",
                curse_name="Rahu in Jupiter's Sign - Spiritual Path Obstruction",
                severity="high",
                houses_involved=[5, 8, 9],
                planets_involved=["Rahu", "Jupiter", "Saturn", "Mars"],
                lords_involved=["Jupiter"],
                description=(
                    "Rahu in Jupiter's sign with Jupiter, Saturn, Mars in 5H, 8H, 9H creates severe curse "
                    "for spiritual seekers. Indicates obstacles on spiritual path, guru curse, karmic bondage, "
                    "and inability to achieve enlightenment or liberation."
                ),
                remedies=[
                    "Guru Puja and Mantra practices",
                    "Jupiter strengthening (Brihaspati Homam)",
                    "Saturn and Mars appeasement",
                    "Rahu shanti rituals",
                    "Intense meditation and yoga",
                    "Seek guidance from enlightened masters"
                ]
            )
            self.add_curse(curse)

    def _check_9l_5h_jupiter_rahu_mars_8h(self) -> None:
        """
        Check: 9L in 5H and Jupiter with Rahu and Mars in 8H
        
        9L in 5H with Jupiter, Rahu, Mars conjunction in 8H.
        """
        nine_lord = self.get_nth_lord(9)
        if not nine_lord:
            return

        nine_l_in_5h = self.is_planet_in_house(nine_lord, 5)
        if not nine_l_in_5h:
            return

        # Check Jupiter, Rahu, Mars in 8H
        jupiter_in_8h = self.is_planet_in_house("Jupiter", 8)
        rahu_in_8h = self.is_planet_in_house("Rahu", 8)
        mars_in_8h = self.is_planet_in_house("Mars", 8)

        if jupiter_in_8h and rahu_in_8h and mars_in_8h:
            curse = CurseRecord(
                curse_type="Spiritual Curse",
                curse_name="9L in 5H with Triple Malefic in 8H - Dharma Failure",
                severity="high",
                houses_involved=[5, 8, 9],
                planets_involved=[nine_lord, "Jupiter", "Rahu", "Mars"],
                lords_involved=[nine_lord],
                description=(
                    "9L in 5H with Jupiter, Rahu, Mars in 8H creates curse affecting dharma and spirituality. "
                    "Indicates failure in spiritual pursuits, guru curse, and inability to follow righteous path. "
                    "Loss of children and spiritual degradation."
                ),
                remedies=[
                    "Perform Maha Mrityunjaya Havan",
                    "Jupiter and Mars appeasement",
                    "Rahu shanti practices",
                    "Dharma Puja and rituals",
                    "Seek ashram and spiritual guidance",
                    "Extreme fasting and meditation"
                ]
            )
            self.add_curse(curse)

    def _check_9l_debilitated_12l_5h_rahu(self) -> None:
        """
        Check: 9L debilitated and 12L in 5H with or aspected by Rahu
        
        Debilitated 9L with 12L in 5H, connected to or aspected by Rahu.
        """
        nine_lord = self.get_nth_lord(9)
        twelve_lord = self.get_nth_lord(12)

        if not (nine_lord and twelve_lord):
            return

        # Check 9L debilitated
        nine_l_debilitated = self.is_planet_debilitated(nine_lord)
        if not nine_l_debilitated:
            return

        # Check 12L in 5H
        twelve_l_in_5h = self.is_planet_in_house(twelve_lord, 5)
        if not twelve_l_in_5h:
            return

        # Check Rahu connection
        rahu_with_12l = self.is_planets_together("Rahu", twelve_lord)
        rahu_aspects_12l = self.is_planet_aspected_by(twelve_lord, ["Rahu"])

        if rahu_with_12l or rahu_aspects_12l:
            curse = CurseRecord(
                curse_type="Spiritual Curse",
                curse_name="9L Debilitated with 12L-Rahu in 5H - Spiritual Prison",
                severity="high",
                houses_involved=[5, 9, 12],
                planets_involved=[nine_lord, twelve_lord, "Rahu"],
                lords_involved=[nine_lord, twelve_lord],
                description=(
                    "Debilitated 9L with 12L in 5H, aspected by Rahu creates curse of spiritual imprisonment. "
                    "Indicates bondage to karmic cycles, inability to attain liberation, and continuous suffering. "
                    "Loss of spiritual progress and enlightenment."
                ),
                remedies=[
                    "Perform extreme meditation and yoga",
                    "Rahu appeasement rituals",
                    "9th house (dharma) strengthening",
                    "12th house remedies",
                    "Seek ashram and spiritual masters",
                    "Recite sacred texts and mantras"
                ]
            )
            self.add_curse(curse)

    def _check_jupiter_debilitated_rahu_5h_5l_trikona(self) -> None:
        """
        Check: Jupiter debilitated, Rahu in Lagna or 5H, 5L in trikona house (bad)
        
        Debilitated Jupiter with Rahu in Lagna/5H and 5L in trikona.
        """
        jupiter_debilitated = self.is_planet_debilitated("Jupiter")
        if not jupiter_debilitated:
            return

        rahu_in_1h = self.is_planet_in_house("Rahu", 1)
        rahu_in_5h = self.is_planet_in_house("Rahu", 5)

        if not (rahu_in_1h or rahu_in_5h):
            return

        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        # Check 5L in trikona (good for 5L) but considering context
        # Here we check if in 5H, 9H position
        five_l_in_trikona = (
            self.is_planet_in_house(five_lord, 5) or 
            self.is_planet_in_house(five_lord, 9)
        )

        if five_l_in_trikona:
            curse = CurseRecord(
                curse_type="Spiritual Curse",
                curse_name="Jupiter Debilitated with Rahu - Spiritual Ignorance",
                severity="high",
                houses_involved=[1, 5, 9],
                planets_involved=["Jupiter", "Rahu", five_lord],
                lords_involved=[five_lord],
                description=(
                    "Debilitated Jupiter with Rahu in Lagna/5H and 5L in trikona creates curse of spiritual "
                    "ignorance. Indicates inability to gain wisdom, false beliefs, deception on spiritual path, "
                    "and karmic confusion."
                ),
                remedies=[
                    "Jupiter strengthening (Brihaspati Homam)",
                    "Guru Puja and mantras",
                    "Rahu appeasement",
                    "Study of Vedas and spiritual texts",
                    "Find true guru for guidance",
                    "Daily meditation and yoga"
                ]
            )
            self.add_curse(curse)

    def _check_jupiter_5l_8h_sun_moon(self) -> None:
        """
        Check: Jupiter as 5L in 8H or 5L in 8H with Sun and Moon
        
        Jupiter or 5L in 8H, possibly with Sun and Moon conjunction.
        """
        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        five_l_in_8h = self.is_planet_in_house(five_lord, 8)
        if not five_l_in_8h:
            return

        # Check Jupiter in 8H if Jupiter is not 5L
        jupiter_in_8h = self.is_planet_in_house("Jupiter", 8)

        # Check Sun and Moon in 8H or with 5L
        sun_in_8h = self.is_planet_in_house("Sun", 8)
        moon_in_8h = self.is_planet_in_house("Moon", 8)
        sun_moon_together = self.is_planets_together("Sun", "Moon")

        if (five_lord == "Jupiter" or jupiter_in_8h) and sun_in_8h and moon_in_8h and sun_moon_together:
            curse = CurseRecord(
                curse_type="Spiritual Curse",
                curse_name="Jupiter/5L in 8H with Sun-Moon - Complete Spiritual Loss",
                severity="high",
                houses_involved=[5, 8],
                planets_involved=[five_lord, "Jupiter", "Sun", "Moon"],
                lords_involved=[five_lord],
                description=(
                    "Jupiter or 5L in 8H with Sun and Moon creates curse causing complete loss of spirituality. "
                    "Indicates occult bondage, loss of progeny, spiritual degradation, and inability to achieve "
                    "any spiritual progress or enlightenment."
                ),
                remedies=[
                    "Perform Maha Mrityunjaya Havan",
                    "Jupiter and Sun protection rituals",
                    "Moon stabilizing practices",
                    "8th house liberation rituals",
                    "Extreme spiritual practices",
                    "Seek enlightened masters for guidance"
                ]
            )
            self.add_curse(curse)

    def _check_jupiter_saturn_navamsha_with_malefics_5l_12h(self) -> None:
        """
        Check: Jupiter in Saturn's navamsha with Saturn and Mars, 5L in 12H
        
        Jupiter in Saturn's navamsha, Saturn and Mars together, 5L in 12H.
        """
        # Simplified check: Jupiter in Saturn's sign
        jupiter_sign = self.get_planet_sign("Jupiter")
        saturn_sign = self.get_planet_sign("Saturn")

        if not (jupiter_sign and saturn_sign and jupiter_sign == saturn_sign):
            return

        # Check Saturn and Mars together
        saturn_mars_together = self.is_planets_together("Saturn", "Mars")
        if not saturn_mars_together:
            return

        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        five_l_in_12h = self.is_planet_in_house(five_lord, 12)

        if five_l_in_12h:
            curse = CurseRecord(
                curse_type="Spiritual Curse",
                curse_name="Jupiter in Saturn Navamsha - Karmic Bondage",
                severity="high",
                houses_involved=[5, 12],
                planets_involved=["Jupiter", "Saturn", "Mars", five_lord],
                lords_involved=[five_lord],
                description=(
                    "Jupiter in Saturn's navamsha with Saturn and Mars, and 5L in 12H creates curse of karmic "
                    "bondage and spiritual imprisonment. Indicates loss of children, occult afflictions, and "
                    "inability to break karmic cycles."
                ),
                remedies=[
                    "Jupiter and Saturn appeasement",
                    "Mars pacification rituals",
                    "12th house liberation practices",
                    "Intense meditation and yoga",
                    "Perform Navagraha Shanti Havan",
                    "Seek spiritual masters for liberation"
                ]
            )
            self.add_curse(curse)

    def _check_jupiter_saturn_lagna_rahu_9h_or_12h(self) -> None:
        """
        Check: Jupiter and Saturn in Lagna with Rahu in 9H OR Jupiter and Rahu in 12H
        
        Complex placements affecting spiritual seekers.
        """
        jupiter_in_1h = self.is_planet_in_house("Jupiter", 1)
        saturn_in_1h = self.is_planet_in_house("Saturn", 1)
        jupiter_saturn_together = self.is_planets_together("Jupiter", "Saturn")

        # Case 1: Jupiter and Saturn in Lagna with Rahu in 9H
        case1 = (
            jupiter_in_1h and saturn_in_1h and jupiter_saturn_together and
            self.is_planet_in_house("Rahu", 9)
        )

        # Case 2: Jupiter and Rahu in 12H
        case2 = (
            self.is_planet_in_house("Jupiter", 12) and
            self.is_planet_in_house("Rahu", 12) and
            self.is_planets_together("Jupiter", "Rahu")
        )

        if case1 or case2:
            curse = CurseRecord(
                curse_type="Spiritual Curse",
                curse_name="Jupiter-Saturn-Rahu Configuration - Childlessness/Spiritual Death",
                severity="high",
                houses_involved=[1, 9, 12],
                planets_involved=["Jupiter", "Saturn", "Rahu"],
                lords_involved=["Jupiter"],
                description=(
                    "Jupiter and Saturn in Lagna with Rahu in 9H or Jupiter and Rahu in 12H creates curse "
                    "of childlessness and spiritual death. Indicates complete loss of progeny, inability to have "
                    "children, spiritual bankruptcy, and life without purpose."
                ),
                remedies=[
                    "Perform Maha Mrityunjaya Havan",
                    "Jupiter strengthening (Brihaspati Homam)",
                    "Saturn appeasement",
                    "Rahu shanti rituals",
                    "Seeking adoption or alternative progeny",
                    "Spiritual transformation and surrender"
                ]
            )
            self.add_curse(curse)
