"""
Mother Curses Detection Module.

Detects curses affecting mother based on specific planetary placements and conjunctions.
Reference: Vedic texts on mother-child relationships and maternal afflictions.
"""

import logging
from typing import Dict, List, Optional
from .curse_detector_base import CurseDetectorBase, CurseRecord

logger = logging.getLogger(__name__)


class MotherCurseDetector(CurseDetectorBase):
    """Detects curses affecting mother based on planetary placements."""

    def __init__(self, planet_data_objs: Dict, house_data_objs: Dict):
        """
        Initialize Mother Curse Detector.
        
        Args:
            planet_data_objs: Dictionary of planet objects
            house_data_objs: Dictionary of house objects
        """
        super().__init__(planet_data_objs, house_data_objs)
        self.detected_curses: List[CurseRecord] = []

    def detect_curses(self) -> List[CurseRecord]:
        """Detect all mother curses."""
        logger.info("Detecting Mother Curses...")
        
        self._check_moon_5l_debilitated_malefics_4h_5h()
        self._check_5l_ill_moon_malefics_lagna_lord_debilitated()
        self._check_5l_ill_malefics_lagna_5h_moon_navamsha_malefic()
        self._check_5l_moon_saturn_rahu_mars_5h_9h()
        self._check_ll_5l_6h_4l_8h_8l_9l_lagna()
        self._check_4l_saturn_rahu_mars_sun_moon_5h()
        self._check_6l_8l_lagna_4l_12h_sun_moon_5h_malefic()
        self._check_ll_pap_kartari_moon_7h_rahu_4h_saturn_5h()
        
        return self.detected_curses

    def _check_moon_5l_debilitated_malefics_4h_5h(self) -> None:
        """
        Check: Moon as 5L debilitated or in pap kartari with malefics in 4H and 5H
        
        Moon as 5L debilitated or in pap kartari (malefic sandwich) with malefics in 4H and 5H.
        """
        five_lord = self.get_nth_lord(5)
        
        if five_lord != "Moon":
            return

        moon_debilitated = self.is_planet_debilitated("Moon")
        moon_house = self.get_planet_house("Moon")

        # Check if moon is in pap kartari (between two malefics)
        if moon_house:
            prev_house = (moon_house - 2) % 12 + 1
            next_house = (moon_house % 12) + 1
            pap_kartari = (
                any(self.is_planet_in_house(m, prev_house) for m in ["Mars", "Saturn", "Rahu", "Sun"]) and
                any(self.is_planet_in_house(m, next_house) for m in ["Mars", "Saturn", "Rahu", "Sun"])
            )
        else:
            pap_kartari = False

        if not (moon_debilitated or pap_kartari):
            return

        # Check malefics in 4H and 5H
        malefic_in_4h = any(self.is_planet_in_house(m, 4) for m in ["Mars", "Saturn", "Rahu", "Sun"])
        malefic_in_5h = any(self.is_planet_in_house(m, 5) for m in ["Mars", "Saturn", "Rahu", "Sun"])

        if malefic_in_4h and malefic_in_5h:
            curse = CurseRecord(
                curse_type="Mother Curse",
                curse_name="Moon as 5L Debilitated - Mother & Children Curse",
                severity="high",
                houses_involved=[4, 5],
                planets_involved=["Moon", "Mars", "Saturn", "Rahu", "Sun"],
                lords_involved=["Moon"],
                description=(
                    "Moon as 5L debilitated or in pap kartari with malefics in 4H and 5H creates severe "
                    "curse affecting mother and children. Indicates mother's illness or death, loss of children, "
                    "and emotional instability in family."
                ),
                remedies=[
                    "Moon strengthening practices (Chandra Puja)",
                    "4th house remedies",
                    "Mother protection rituals",
                    "Milk and white items charity",
                    "Monday fasts and practices",
                    "Perform Durga Saptashati for family protection"
                ]
            )
            self.add_curse(curse)

    def _check_5l_ill_moon_malefics_lagna_lord_debilitated(self) -> None:
        """
        Check: 5L ill-placed, Moon with malefics, Lagna lord debilitated
        
        5L in bad house, Moon conjunct with malefics, and debilitated Lagna lord.
        """
        five_lord = self.get_nth_lord(5)
        lagna_lord = self.get_nth_lord(1)

        if not (five_lord and lagna_lord):
            return

        # Check 5L ill-placed (6/8/12)
        five_l_bad = any(self.is_planet_in_house(five_lord, h) for h in [6, 8, 12])

        if not five_l_bad:
            return

        # Check Moon with malefics
        moon_malefic = any(
            self.is_planets_together("Moon", m) for m in ["Mars", "Saturn", "Rahu", "Sun"]
        )

        # Check Lagna lord debilitated
        lagna_lord_debilitated = self.is_planet_debilitated(lagna_lord)

        if moon_malefic and lagna_lord_debilitated:
            curse = CurseRecord(
                curse_type="Mother Curse",
                curse_name="5L Ill-Placed with Moon-Malefics - Mother Health Curse",
                severity="high",
                houses_involved=[1, 5, 6, 8, 12],
                planets_involved=["Moon", "Mars", "Saturn", "Rahu", "Sun", five_lord, lagna_lord],
                lords_involved=[five_lord, lagna_lord],
                description=(
                    "5L ill-placed with Moon conjunct malefics and debilitated Lagna lord creates curse "
                    "affecting mother's health and children's well-being. Indicates chronic maternal illness, "
                    "psychological problems, and separation from mother."
                ),
                remedies=[
                    "Moon stabilizing practices",
                    "Mother health protection rituals",
                    "Lagna lord strengthening practices",
                    "Emotional healing and therapy",
                    "Regular mother worship and care",
                    "Perform Hanuman Chalisa for family protection"
                ]
            )
            self.add_curse(curse)

    def _check_5l_ill_malefics_lagna_5h_moon_navamsha_malefic(self) -> None:
        """
        Check: 5L ill-placed, malefics in Lagna and 5H, Moon in navamsha of malefic
        
        5L in bad house with malefics in Lagna and 5H and Moon in malefic's navamsha.
        """
        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        # Check 5L ill-placed
        five_l_bad = any(self.is_planet_in_house(five_lord, h) for h in [6, 8, 12])
        if not five_l_bad:
            return

        # Check malefics in Lagna and 5H
        malefic_in_1h = any(self.is_planet_in_house(m, 1) for m in ["Mars", "Saturn", "Rahu", "Sun"])
        malefic_in_5h = any(self.is_planet_in_house(m, 5) for m in ["Mars", "Saturn", "Rahu", "Sun"])

        if not (malefic_in_1h and malefic_in_5h):
            return

        # Check Moon in navamsha of malefic (Moon in sign of malefic - simplified check)
        moon_sign = self.get_planet_sign("Moon")
        mars_sign = self.get_planet_sign("Mars")
        saturn_sign = self.get_planet_sign("Saturn")
        rahu_sign = self.get_planet_sign("Rahu")

        moon_in_malefic_sign = moon_sign in [mars_sign, saturn_sign, rahu_sign]

        if moon_in_malefic_sign:
            curse = CurseRecord(
                curse_type="Mother Curse",
                curse_name="5L Ill-Placed with Malefic Placement - Mother Suffering",
                severity="high",
                houses_involved=[1, 5, 6, 8, 12],
                planets_involved=["Moon", "Mars", "Saturn", "Rahu", "Sun", five_lord],
                lords_involved=[five_lord],
                description=(
                    "5L ill-placed with malefics in Lagna and 5H and Moon in malefic's navamsha creates "
                    "severe curse for mother and children. Indicates mother's mental/physical suffering, "
                    "children's chronic illnesses, and complete family dysfunction."
                ),
                remedies=[
                    "Perform Maha Mrityunjaya Havan",
                    "Moon and malefic appeasement",
                    "Mother healing rituals",
                    "Regular spiritual practices",
                    "Seek ashram or spiritual guidance",
                    "Complete life transformation for family welfare"
                ]
            )
            self.add_curse(curse)

    def _check_5l_moon_saturn_rahu_mars_5h_9h(self) -> None:
        """
        Check: 5L with Moon, Saturn, Rahu, Mars in 5H or 9H
        
        5L conjunct with Moon and multiple malefics (Saturn, Rahu, Mars) in 5H or 9H.
        """
        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        # Check 5L with Moon
        five_l_moon = self.is_planets_together(five_lord, "Moon")
        if not five_l_moon:
            return

        # Check for Saturn, Rahu, Mars in 5H or 9H
        malefics = ["Saturn", "Rahu", "Mars"]
        malefics_in_5h_9h = any(
            self.is_planet_in_house(m, 5) or self.is_planet_in_house(m, 9)
            for m in malefics
        )

        if not malefics_in_5h_9h:
            return

        curse = CurseRecord(
            curse_type="Mother Curse",
            curse_name="5L with Moon & Malefics in 5H/9H - Complete Progeny Loss",
            severity="high",
            houses_involved=[5, 9],
            planets_involved=[five_lord, "Moon", "Saturn", "Rahu", "Mars"],
            lords_involved=[five_lord],
            description=(
                "5L with Moon and Saturn, Rahu, Mars in 5H or 9H creates severe curse affecting mother "
                "and complete loss of progeny. Indicates miscarriages, child deaths, or inability to conceive. "
                "Mother faces extreme suffering and loss."
            ),
            remedies=[
                "Perform Maha Mrityunjaya Havan",
                "Saturn, Rahu, Mars appeasement",
                "Mother protection Puja",
                "5th house purification rituals",
                "Extreme fasting and penance",
                "Seek blessings from enlightened masters"
            ]
        )
        self.add_curse(curse)

    def _check_ll_5l_6h_4l_8h_8l_9l_lagna(self) -> None:
        """
        Check: LL and 5L in 6H, 4L in 8H, 8L and 9L in Lagna
        
        Complex placement with LL-5L in 6H, 4L in 8H, and 8L-9L in Lagna.
        """
        lagna_lord = self.get_nth_lord(1)
        five_lord = self.get_nth_lord(5)
        four_lord = self.get_nth_lord(4)
        eight_lord = self.get_nth_lord(8)
        nine_lord = self.get_nth_lord(9)

        if not all([lagna_lord, five_lord, four_lord, eight_lord, nine_lord]):
            return

        # Check LL and 5L in 6H
        ll_in_6h = self.is_planet_in_house(lagna_lord, 6)
        five_l_in_6h = self.is_planet_in_house(five_lord, 6)

        if not (ll_in_6h and five_l_in_6h):
            return

        # Check 4L in 8H
        four_l_in_8h = self.is_planet_in_house(four_lord, 8)
        if not four_l_in_8h:
            return

        # Check 8L and 9L in Lagna
        eight_l_in_1h = self.is_planet_in_house(eight_lord, 1)
        nine_l_in_1h = self.is_planet_in_house(nine_lord, 1)

        if eight_l_in_1h and nine_l_in_1h:
            curse = CurseRecord(
                curse_type="Mother Curse",
                curse_name="Complex Placement - Complete Family Curse",
                severity="high",
                houses_involved=[1, 4, 6, 8, 9],
                planets_involved=[lagna_lord, five_lord, four_lord, eight_lord, nine_lord],
                lords_involved=[lagna_lord, five_lord, four_lord, eight_lord, nine_lord],
                description=(
                    "LL and 5L in 6H with 4L in 8H and 8L, 9L in Lagna creates extreme family curse. "
                    "Indicates mother's death or complete separation, loss of all children, family destruction, "
                    "and complete life upheaval."
                ),
                remedies=[
                    "Perform Navagraha Shanti Havan",
                    "Ancestral puja and Pitru rituals",
                    "Mother blessing ceremonies",
                    "Extreme fasting and penance",
                    "Seek ashram and spiritual guidance",
                    "Complete transformation and rebirth"
                ]
            )
            self.add_curse(curse)

    def _check_4l_saturn_rahu_mars_sun_moon_5h(self) -> None:
        """
        Check: 4L with Saturn, Rahu, Mars & Sun, Moon in 5H
        
        4L conjunct Saturn, Rahu, Mars with Sun and Moon both in 5H.
        """
        four_lord = self.get_nth_lord(4)
        if not four_lord:
            return

        # Check 4L with Saturn, Rahu, Mars
        four_l_saturn = self.is_planets_together(four_lord, "Saturn")
        four_l_rahu = self.is_planets_together(four_lord, "Rahu")
        four_l_mars = self.is_planets_together(four_lord, "Mars")

        malefics_with_4l = four_l_saturn or four_l_rahu or four_l_mars

        if not malefics_with_4l:
            return

        # Check Sun and Moon in 5H
        sun_in_5h = self.is_planet_in_house("Sun", 5)
        moon_in_5h = self.is_planet_in_house("Moon", 5)

        if sun_in_5h and moon_in_5h:
            curse = CurseRecord(
                curse_type="Mother Curse",
                curse_name="4L with Malefics & Sun-Moon in 5H - Mother Death Curse",
                severity="high",
                houses_involved=[4, 5],
                planets_involved=[four_lord, "Saturn", "Rahu", "Mars", "Sun", "Moon"],
                lords_involved=[four_lord],
                description=(
                    "4L with Saturn, Rahu, Mars and Sun, Moon in 5H creates severe mother curse. "
                    "Indicates mother's early death or critical illness, loss of children, and complete "
                    "family separation. Home and family foundation destroyed."
                ),
                remedies=[
                    "Perform Maha Mrityunjaya Havan for mother",
                    "4th house protection rituals",
                    "Mother blessing and memorial ceremonies",
                    "Sun and Moon stabilizing practices",
                    "Extreme penance and fasting",
                    "Seek spiritual masters for family healing"
                ]
            )
            self.add_curse(curse)

    def _check_6l_8l_lagna_4l_12h_sun_moon_5h_malefic(self) -> None:
        """
        Check: 6L & 8L in Lagna, 4L in 12H, Sun & Moon in 5H with malefic
        
        6L and 8L in Lagna with 4L in 12H and Sun, Moon in 5H with malefic.
        """
        six_lord = self.get_nth_lord(6)
        eight_lord = self.get_nth_lord(8)
        four_lord = self.get_nth_lord(4)

        if not (six_lord and eight_lord and four_lord):
            return

        # Check 6L and 8L in Lagna
        six_l_in_1h = self.is_planet_in_house(six_lord, 1)
        eight_l_in_1h = self.is_planet_in_house(eight_lord, 1)

        if not (six_l_in_1h and eight_l_in_1h):
            return

        # Check 4L in 12H
        four_l_in_12h = self.is_planet_in_house(four_lord, 12)
        if not four_l_in_12h:
            return

        # Check Sun and Moon in 5H with malefic
        sun_in_5h = self.is_planet_in_house("Sun", 5)
        moon_in_5h = self.is_planet_in_house("Moon", 5)
        malefic_in_5h = any(self.is_planet_in_house(m, 5) for m in ["Mars", "Saturn", "Rahu"])

        if sun_in_5h and moon_in_5h and malefic_in_5h:
            curse = CurseRecord(
                curse_type="Mother Curse",
                curse_name="6L-8L in Lagna - Extreme Family Destruction",
                severity="high",
                houses_involved=[1, 4, 5, 12],
                planets_involved=[six_lord, eight_lord, four_lord, "Sun", "Moon", "Mars", "Saturn", "Rahu"],
                lords_involved=[six_lord, eight_lord, four_lord],
                description=(
                    "6L and 8L in Lagna with 4L in 12H and Sun, Moon in 5H with malefic creates extreme "
                    "family curse. Complete destruction of mother, children, home, and family bonds. "
                    "Indicates multiple losses and complete life transformation."
                ),
                remedies=[
                    "Perform Navagraha Shanti Havan",
                    "Extreme fasting and meditation",
                    "Family healing and purification rituals",
                    "Mother and children protection Puja",
                    "Seek ashram and spiritual transformation",
                    "Long-term spiritual practices"
                ]
            )
            self.add_curse(curse)

    def _check_ll_pap_kartari_moon_7h_rahu_4h_saturn_5h(self) -> None:
        """
        Check: LL in pap kartari, weak Moon in 7H, Rahu in 4H, Saturn in 5H
        
        Lagna lord in pap kartari with weak Moon in 7H, Rahu in 4H, Saturn in 5H.
        """
        lagna_lord = self.get_nth_lord(1)
        if not lagna_lord:
            return

        # Check Lagna lord in pap kartari
        lagna_lord_house = self.get_planet_house(lagna_lord)
        if lagna_lord_house:
            prev_house = (lagna_lord_house - 2) % 12 + 1
            next_house = (lagna_lord_house % 12) + 1
            pap_kartari = (
                any(self.is_planet_in_house(m, prev_house) for m in ["Mars", "Saturn", "Rahu", "Sun"]) and
                any(self.is_planet_in_house(m, next_house) for m in ["Mars", "Saturn", "Rahu", "Sun"])
            )
        else:
            pap_kartari = False

        if not pap_kartari:
            return

        # Check weak Moon in 7H
        moon_in_7h = self.is_planet_in_house("Moon", 7)
        moon_debilitated = self.is_planet_debilitated("Moon")

        if not (moon_in_7h and moon_debilitated):
            return

        # Check Rahu in 4H and Saturn in 5H
        rahu_in_4h = self.is_planet_in_house("Rahu", 4)
        saturn_in_5h = self.is_planet_in_house("Saturn", 5)

        if rahu_in_4h and saturn_in_5h:
            curse = CurseRecord(
                curse_type="Mother Curse",
                curse_name="LL Pap Kartari with Moon-Rahu-Saturn Configuration",
                severity="high",
                houses_involved=[1, 4, 5, 7],
                planets_involved=[lagna_lord, "Moon", "Rahu", "Saturn"],
                lords_involved=[lagna_lord],
                description=(
                    "Lagna lord in pap kartari with weak Moon in 7H, Rahu in 4H, Saturn in 5H creates "
                    "severe mother curse. Indicates mother's ill-health, emotional disturbance, relationship "
                    "problems, and loss of children. Complete family unhappiness."
                ),
                remedies=[
                    "Lagna lord strengthening practices",
                    "Moon protection and stabilizing",
                    "Rahu shanti rituals",
                    "Saturn appeasement",
                    "Mother care and blessing ceremonies",
                    "Regular spiritual practices for family harmony"
                ]
            )
            self.add_curse(curse)
