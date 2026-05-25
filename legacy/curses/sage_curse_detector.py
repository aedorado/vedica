"""
Sage Curses Detection Module.

Detects curses from sages based on specific planetary placements and conjunctions.
Reference: Ancient Vedic texts on nakshatras and planetary combinations causing suffering.
"""

import logging
from typing import Dict, List, Optional
from .curse_detector_base import CurseDetectorBase, CurseRecord

logger = logging.getLogger(__name__)


class SageCurseDetector(CurseDetectorBase):
    """Detects curses from sages based on planetary placements."""

    def __init__(self, planet_data_objs: Dict, house_data_objs: Dict):
        """
        Initialize Sage Curse Detector.
        
        Args:
            planet_data_objs: Dictionary of planet objects
            house_data_objs: Dictionary of house objects
        """
        super().__init__(planet_data_objs, house_data_objs)
        self.detected_curses: List[CurseRecord] = []

    def detect_curses(self) -> List[CurseRecord]:
        """Detect all sage curses."""
        logger.info("Detecting Sage Curses...")
        
        self._check_debilitated_jupiter_5h_lagna_bad_lords()
        self._check_debilitated_jupiter_5l_in_8h()
        self._check_5l_in_8h_with_sun_moon()
        self._check_5l_in_12h_jupiter_with_saturn_mars()
        self._check_jupiter_saturn_lagna_rahu_9h()
        self._check_jupiter_rahu_in_12h()
        self._check_debilitated_9l_12l_in_5h()
        self._check_9l_in_5h_jupiter_with_rahu_mars_in_8h()
        self._check_9l_in_8h_with_guru_shani_mangal()
        
        return self.detected_curses

    def _check_debilitated_jupiter_5h_lagna_bad_lords(self) -> None:
        """
        Check: Deb Ju, Ra in 5H / Lagna & 5L in 6/8/12H
        
        A debilitated Jupiter with Rahu in 5H or Lagna, and 5L placed in 
        6H/8H/12H creates a curse causing loss of children or progeny issues.
        """
        # Check if Jupiter is debilitated
        if not self.is_planet_debilitated("Jupiter"):
            return

        # Check Rahu placement
        rahu_in_5h = self.is_planet_in_house("Rahu", 5)
        rahu_in_1h = self.is_planet_in_house("Rahu", 1)
        
        if not (rahu_in_5h or rahu_in_1h):
            return

        # Get 5L (5th lord) from the sign in 5th house
        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        # Check 5L placement in bad houses
        five_l_in_bad_house = self.is_planet_in_houses(five_lord, [6, 8, 12])

        if five_l_in_bad_house:
            curse = CurseRecord(
                curse_type="Sage Curse",
                curse_name="Debilitated Jupiter with Rahu - Progeny Curse",
                severity="high",
                houses_involved=[1, 5, 6, 8, 12],
                planets_involved=["Jupiter", "Rahu", five_lord],
                lords_involved=[five_lord],
                description=(
                    "Debilitated Jupiter with Rahu in 5H or Lagna, combined with "
                    "5L in 6/8/12H causes severe progeny issues, loss of children, "
                    "and inability to procreate. This is a curse from sages upon actions "
                    "affecting dharma or divine progeny plans."
                ),
                remedies=[
                    "Chant Jupiter mantras (Bhaskar Mantra)",
                    "Perform Rahu shanti rituals",
                    "Worship Lakshmi for progeny blessings",
                    "Pilgrimage to Ujjain or Dwarka"
                ]
            )
            self.add_curse(curse)

    def _check_debilitated_jupiter_5l_in_8h(self) -> None:
        """
        Check: Ju is 5L placed in 8H with Sun & Moon
        
        Jupiter as 5L placed in 8H with Sun and Moon indicates severe progeny curse
        from sage Atri or similar deities overseeing family lineage.
        """
        # Check if Jupiter is the 5th lord and is in 8H
        five_lord = self.get_nth_lord(5)
        if five_lord != "Jupiter":
            return
            
        five_lord_in_8h = self.is_planet_in_house("Jupiter", 8)
        if not five_lord_in_8h:
            return

        sun_in_8h = self.is_planet_in_house("Sun", 8)
        moon_in_8h = self.is_planet_in_house("Moon", 8)

        if sun_in_8h and moon_in_8h:
            curse = CurseRecord(
                curse_type="Sage Curse",
                curse_name="Jupiter 5L in 8H with Sun & Moon - Severe Progeny Curse",
                severity="high",
                houses_involved=[5, 8],
                planets_involved=["Jupiter", "Sun", "Moon"],
                lords_involved=["Jupiter"],
                description=(
                    "Jupiter as 5L placed in 8H conjunct with Sun and Moon causes "
                    "complete annihilation of progeny line. This is considered a curse "
                    "from celestial sages protecting dharma. Indicates childlessness, "
                    "miscarriages, or death of children."
                ),
                remedies=[
                    "Hanuman Chalisa recitation daily",
                    "Offer milk to sacred cows",
                    "Worship Durga for family protection",
                    "Fast on Mondays and Thursdays"
                ]
            )
            self.add_curse(curse)

    def _check_5l_in_8h_with_sun_moon(self) -> None:
        """
        Check: 5L placed in 8H with Sun and Moon
        
        General check for 5L in 8H with both Sun and Moon, creating progeny curse.
        """
        # Get the 5L
        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        five_l_in_8h = self.is_planet_in_house(five_lord, 8)
        if not five_l_in_8h:
            return

        sun_in_8h = self.is_planet_in_house("Sun", 8)
        moon_in_8h = self.is_planet_in_house("Moon", 8)

        if sun_in_8h and moon_in_8h:
            curse = CurseRecord(
                curse_type="Sage Curse",
                curse_name="5L in 8H with Sun & Moon - Progeny Destruction",
                severity="high",
                houses_involved=[5, 8],
                planets_involved=[five_lord, "Sun", "Moon"],
                lords_involved=[five_lord],
                description=(
                    "5L placed in 8H with conjunction of Sun and Moon creates "
                    "a severe curse affecting progeny. This combination is said to "
                    "result from past-life actions against children or dharma."
                ),
                remedies=[
                    "Maha Mrityunjaya Mantra recitation",
                    "Offering to Goddess Parvati",
                    "Regular temple visits",
                    "Service to orphaned children"
                ]
            )
            self.add_curse(curse)

    def _check_5l_in_12h_jupiter_with_saturn_mars(self) -> None:
        """
        Check: 5L in 12H, Ju conjunct with Sa & Ma, Ju in Navamsha of Sa
        
        5L in 12H with Jupiter conjunct Saturn and Mars, Jupiter in Saturn's navamsha,
        indicates progeny loss and spiritual obstacles.
        """
        # Get the 5L
        five_lord = self.get_nth_lord(5)
        if not five_lord:
            return

        five_l_in_12h = self.is_planet_in_house(five_lord, 12)
        if not five_l_in_12h:
            return

        # Check Jupiter conditions
        jupiter_in_12h = self.is_planet_in_house("Jupiter", 12)
        jupiter_with_saturn = self.is_planets_together("Jupiter", "Saturn")
        jupiter_with_mars = self.is_planets_together("Jupiter", "Mars")

        if jupiter_in_12h and jupiter_with_saturn and jupiter_with_mars:
            curse = CurseRecord(
                curse_type="Sage Curse",
                curse_name="5L in 12H - Jupiter with Saturn & Mars",
                severity="high",
                houses_involved=[5, 12],
                planets_involved=["Jupiter", "Saturn", "Mars", five_lord],
                lords_involved=[five_lord, "Jupiter"],
                description=(
                    "5L in 12H with Jupiter conjunct Saturn and Mars creates "
                    "progeny loss and spiritual bondage. The placement in Saturn's "
                    "navamsha amplifies karmic debts. This curse manifests as "
                    "inability to have children or children facing severe hardships."
                ),
                remedies=[
                    "Jupiter Brihaspati Homam",
                    "Wear Jupiter yellow sapphire",
                    "Saturn appeasement rituals (Shani Puja)",
                    "Donate to temples and charities"
                ]
            )
            self.add_curse(curse)

    def _check_jupiter_saturn_lagna_rahu_9h(self) -> None:
        """
        Check: Ju & Sa in Lagna & Ra in 9H
        
        Jupiter and Saturn together in Lagna with Rahu in 9H creates a curse
        affecting fortune, guidance, and spiritual path.
        """
        jupiter_in_1h = self.is_planet_in_house("Jupiter", 1)
        saturn_in_1h = self.is_planet_in_house("Saturn", 1)
        rahu_in_9h = self.is_planet_in_house("Rahu", 9)

        if jupiter_in_1h and saturn_in_1h and rahu_in_9h:
            curse = CurseRecord(
                curse_type="Sage Curse",
                curse_name="Jupiter & Saturn in Lagna - Rahu in 9H Curse",
                severity="medium",
                houses_involved=[1, 9],
                planets_involved=["Jupiter", "Saturn", "Rahu"],
                lords_involved=["Jupiter", "Saturn"],
                description=(
                    "Jupiter and Saturn conjunction in Lagna with Rahu in 9H creates "
                    "a curse affecting wisdom, fortune, and spiritual knowledge. "
                    "The native faces obstacles in achieving higher wisdom, guidance "
                    "from gurus is difficult, and there's confusion in life direction."
                ),
                remedies=[
                    "Guru Puja and Mantras",
                    "Study sacred texts (Vedas/Upanishads)",
                    "Meditation on Rahu (tantric practices)",
                    "Service to elderly teachers and gurus"
                ]
            )
            self.add_curse(curse)

    def _check_jupiter_rahu_in_12h(self) -> None:
        """
        Check: Ju with Ra in 12H
        
        Jupiter with Rahu in 12H creates a curse of isolation, loss of resources,
        and spiritual imprisonment.
        """
        jupiter_with_rahu = self.is_planets_together("Jupiter", "Rahu")
        jupiter_in_12h = self.is_planet_in_house("Jupiter", 12)
        rahu_in_12h = self.is_planet_in_house("Rahu", 12)

        if jupiter_with_rahu and jupiter_in_12h and rahu_in_12h:
            curse = CurseRecord(
                curse_type="Sage Curse",
                curse_name="Jupiter with Rahu in 12H - Spiritual Curse",
                severity="high",
                houses_involved=[12],
                planets_involved=["Jupiter", "Rahu"],
                lords_involved=["Jupiter"],
                description=(
                    "Jupiter with Rahu in 12H creates a severe curse of spiritual "
                    "imprisonment, loss of prosperity, and exile (physical or mental). "
                    "The native experiences loss of resources, difficulty in foreign "
                    "lands, and obstacles on spiritual path. Said to result from "
                    "non-payment of debts to sages or betrayal of spiritual teachers."
                ),
                remedies=[
                    "Recite Navagraha Stotra",
                    "12th house remedies (Vyaya Sthana)",
                    "Charity and donations (12th house remedy)",
                    "Meditation and ashram stays"
                ]
            )
            self.add_curse(curse)

    def _check_debilitated_9l_12l_in_5h(self) -> None:
        """
        Check: Deb 9L & 12L in 5H with or aspected by Ra
        
        Debilitated 9L and 12L together in 5H, aspected by Rahu, creates a curse
        affecting fortune, father's health, and karmic debts.
        """
        # Get 9L and 12L
        nine_lord = self.get_nth_lord(9)
        twelve_lord = self.get_nth_lord(12)

        if not nine_lord or not twelve_lord:
            return

        nine_l_in_5h = self.is_planet_in_house(nine_lord, 5)
        twelve_l_in_5h = self.is_planet_in_house(twelve_lord, 5)

        if not (nine_l_in_5h and twelve_l_in_5h):
            return

        # Check if either is debilitated
        nine_l_debilitated = self.is_planet_debilitated(nine_lord)
        twelve_l_debilitated = self.is_planet_debilitated(twelve_lord)

        # Check Rahu aspect
        rahu_aspect = self.is_planet_aspected_by(nine_lord, ["Rahu"]) or \
                     self.is_planet_aspected_by(twelve_lord, ["Rahu"])

        if (nine_l_debilitated or twelve_l_debilitated) and rahu_aspect:
            curse = CurseRecord(
                curse_type="Sage Curse",
                curse_name="Debilitated 9L & 12L in 5H - Karmic Curse",
                severity="high",
                houses_involved=[5, 9, 12],
                planets_involved=[nine_lord, twelve_lord, "Rahu"],
                lords_involved=[nine_lord, twelve_lord],
                description=(
                    "Debilitated 9L and 12L in 5H, aspected by Rahu, creates a "
                    "curse affecting father's longevity, karmic debts, and children's "
                    "well-being. This indicates past-life non-fulfillment of duties "
                    "to parents or dharma. The curse manifests through family suffering."
                ),
                remedies=[
                    "Pitru Shanti (ancestral appeasement)",
                    "Fast on New Moon and Full Moon",
                    "Support elderly parents and teachers",
                    "Perform Pitra Tarpan rituals"
                ]
            )
            self.add_curse(curse)

    def _check_9l_in_5h_jupiter_with_rahu_mars_in_8h(self) -> None:
        """
        Check: 9L in 5H, Ju with Ra, Ma in 8H
        
        9L in 5H with Jupiter conjunct Rahu and Mars in 8H creates a curse
        affecting dharma, children, and longevity.
        """
        # Get 9L
        nine_lord = self.get_nth_lord(9)
        if not nine_lord:
            return

        nine_l_in_5h = self.is_planet_in_house(nine_lord, 5)
        if not nine_l_in_5h:
            return

        jupiter_rahu_together = self.is_planets_together("Jupiter", "Rahu")
        mars_in_8h = self.is_planet_in_house("Mars", 8)

        if jupiter_rahu_together and mars_in_8h:
            curse = CurseRecord(
                curse_type="Sage Curse",
                curse_name="9L in 5H - Jupiter with Rahu & Mars in 8H",
                severity="high",
                houses_involved=[5, 8, 9],
                planets_involved=["Jupiter", "Rahu", "Mars", nine_lord],
                lords_involved=[nine_lord, "Jupiter"],
                description=(
                    "9L in 5H with Jupiter conjunct Rahu and Mars in 8H creates "
                    "a curse affecting dharmic duty, progeny, and father's life. "
                    "The native faces obstacles in fulfilling spiritual duties and "
                    "experiences loss of children or their suffering."
                ),
                remedies=[
                    "Hanuman Mantra recitation",
                    "Mars appeasement (Mangal Puja)",
                    "Daily Dharma practice",
                    "Pilgrimage to holy sites"
                ]
            )
            self.add_curse(curse)

    def _check_9l_in_8h_with_guru_shani_mangal(self) -> None:
        """
        Check: 9L in 8H, Ju, Sa, Ma together in 5H, Ra in sign of Ju
        
        9L in 8H with Jupiter, Saturn, Mars together in 5H and Rahu in Jupiter's sign
        creates a severe curse affecting father, dharma, and family.
        """
        # Get 9L
        nine_lord = self.get_nth_lord(9)
        if not nine_lord:
            return

        nine_l_in_8h = self.is_planet_in_house(nine_lord, 8)
        if not nine_l_in_8h:
            return

        # Check if Jupiter, Saturn, Mars are together in 5H
        guru_shani_mangal_together = self.are_multiple_planets_together(
            ["Jupiter", "Saturn", "Mars"]
        )
        guru_shani_mangal_in_5h = (
            self.is_planet_in_house("Jupiter", 5) and
            self.is_planet_in_house("Saturn", 5) and
            self.is_planet_in_house("Mars", 5)
        )

        if not guru_shani_mangal_in_5h:
            return

        # Check if Rahu is in Jupiter's sign
        jupiter_sign = self.get_planet_sign("Jupiter")
        rahu_sign = self.get_planet_sign("Rahu")

        if jupiter_sign and rahu_sign and jupiter_sign == rahu_sign:
            curse = CurseRecord(
                curse_type="Sage Curse",
                curse_name="9L in 8H - Triple Malefic in 5H - Rahu in Jupiter's Sign",
                severity="high",
                houses_involved=[5, 8, 9],
                planets_involved=["Jupiter", "Saturn", "Mars", "Rahu", nine_lord],
                lords_involved=[nine_lord],
                description=(
                    "9L in 8H with Jupiter, Saturn, Mars conjunction in 5H and "
                    "Rahu in Jupiter's sign creates the most severe curse affecting "
                    "father's death/suffering, complete destruction of progeny, and "
                    "dharmic collapse. This is said to result from killing or harming "
                    "a sage in past life or severe betrayal of spiritual teacher."
                ),
                remedies=[
                    "Perform Maha Mrityunjaya Havan",
                    "Extreme fasting and penance",
                    "Seek blessings from living sages/gurus",
                    "Complete life transformation and dharma realignment",
                    "Recite Devi Mahatmya or Shiva Purana"
                ]
            )
            self.add_curse(curse)
