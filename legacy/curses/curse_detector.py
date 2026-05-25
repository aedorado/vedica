"""
Main Curse Detection Module.

Coordinates detection of various types of curses including curses from sages,
women, snakes, brothers, and other celestial entities.
"""

import logging
from typing import Dict, List, Optional
from .sage_curse_detector import SageCurseDetector
from .brother_curse_detector import BrotherCurseDetector
from .spouse_curse_detector import SpouseCurseDetector
from .snake_curse_detector import SnakeCurseDetector
from .father_curse_detector import FatherCurseDetector
from .mother_curse_detector import MotherCurseDetector
from .spiritual_curse_detector import SpiritualCurseDetector
from .evil_spirit_curse_detector import EvilSpiritCurseDetector
from .curse_detector_base import CurseRecord

logger = logging.getLogger(__name__)


class CurseDetector:
    """Main coordinator for all curse detection."""

    def __init__(self, planet_data_objs: Dict, house_data_objs: Dict):
        """
        Initialize the main curse detector.
        
        Args:
            planet_data_objs: Dictionary of planet objects
            house_data_objs: Dictionary of house objects
        """
        self.planet_data_objs = planet_data_objs
        self.house_data_objs = house_data_objs
        self.all_curses: Dict[str, List[CurseRecord]] = {}

    def detect_all_curses(self) -> None:
        """Detect all types of curses in the chart."""
        logger.info("Starting comprehensive curse detection analysis...")
        
        print("\n🧙 Curse Detection Analysis")
        print("=" * 60)
        
        # Detect curses from sages
        print("\n1️⃣  Detecting Sage Curses...")
        sage_curses = self._detect_sage_curses()
        self.all_curses["Sage Curses"] = sage_curses

        # Detect curses from brothers
        print("\n2️⃣  Detecting Brother Curses...")
        brother_curses = self._detect_brother_curses()
        self.all_curses["Brother Curses"] = brother_curses

        # Detect curses affecting spouse/wife
        print("\n3️⃣  Detecting Spouse/Wife Curses...")
        spouse_curses = self._detect_spouse_curses()
        self.all_curses["Spouse Curses"] = spouse_curses

        # Detect curses from snakes
        print("\n4️⃣  Detecting Snake Curses...")
        snake_curses = self._detect_snake_curses()
        self.all_curses["Snake Curses"] = snake_curses

        # Detect curses from father
        print("\n5️⃣  Detecting Father Curses...")
        father_curses = self._detect_father_curses()
        self.all_curses["Father Curses"] = father_curses

        # Detect curses from mother
        print("\n6️⃣  Detecting Mother Curses...")
        mother_curses = self._detect_mother_curses()
        self.all_curses["Mother Curses"] = mother_curses

        # Detect curses from spiritual persons/saints
        print("\n7️⃣  Detecting Spiritual Person Curses...")
        spiritual_curses = self._detect_spiritual_curses()
        self.all_curses["Spiritual Person Curses"] = spiritual_curses

        # Detect curses from evil spirits
        print("\n8️⃣  Detecting Evil Spirit Curses...")
        evil_spirit_curses = self._detect_evil_spirit_curses()
        self.all_curses["Evil Spirit Curses"] = evil_spirit_curses

        self._print_curse_summary()

    def _detect_sage_curses(self) -> List[CurseRecord]:
        """Detect curses from sages."""
        sage_detector = SageCurseDetector(self.planet_data_objs, self.house_data_objs)
        curses = sage_detector.detect_curses()
        sage_detector.print_curse_summary()
        return curses

    def _detect_brother_curses(self) -> List[CurseRecord]:
        """Detect curses from brothers."""
        brother_detector = BrotherCurseDetector(self.planet_data_objs, self.house_data_objs)
        curses = brother_detector.detect_curses()
        brother_detector.print_curse_summary()
        return curses

    def _detect_spouse_curses(self) -> List[CurseRecord]:
        """Detect curses affecting spouse/wife."""
        spouse_detector = SpouseCurseDetector(self.planet_data_objs, self.house_data_objs)
        curses = spouse_detector.detect_curses()
        spouse_detector.print_curse_summary()
        return curses

    def _detect_snake_curses(self) -> List[CurseRecord]:
        """Detect curses from snakes."""
        snake_detector = SnakeCurseDetector(self.planet_data_objs, self.house_data_objs)
        curses = snake_detector.detect_curses()
        snake_detector.print_curse_summary()
        return curses

    def _detect_father_curses(self) -> List[CurseRecord]:
        """Detect curses from father."""
        father_detector = FatherCurseDetector(self.planet_data_objs, self.house_data_objs)
        curses = father_detector.detect_curses()
        father_detector.print_curse_summary()
        return curses

    def _detect_mother_curses(self) -> List[CurseRecord]:
        """Detect curses from mother."""
        mother_detector = MotherCurseDetector(self.planet_data_objs, self.house_data_objs)
        curses = mother_detector.detect_curses()
        mother_detector.print_curse_summary()
        return curses

    def _detect_spiritual_curses(self) -> List[CurseRecord]:
        """Detect curses from spiritual persons/saints."""
        spiritual_detector = SpiritualCurseDetector(self.planet_data_objs, self.house_data_objs)
        curses = spiritual_detector.detect_curses()
        spiritual_detector.print_curse_summary()
        return curses

    def _detect_evil_spirit_curses(self) -> List[CurseRecord]:
        """Detect curses from evil spirits."""
        evil_spirit_detector = EvilSpiritCurseDetector(self.planet_data_objs, self.house_data_objs)
        curses = evil_spirit_detector.detect_curses()
        evil_spirit_detector.print_curse_summary()
        return curses

    def _print_curse_summary(self) -> None:
        """Print a comprehensive summary of all detected curses."""
        print("\n" + "=" * 60)
        print("📊 CURSE DETECTION SUMMARY")
        print("=" * 60)
        
        total_curses = sum(len(curses) for curses in self.all_curses.values())
        
        if total_curses == 0:
            print("\n✅ No major curses detected in the chart.")
            print("\nThis indicates good karmic standing and divine blessings.")
        else:
            print(f"\n⚠️  Total Curses Detected: {total_curses}")
            
            for curse_type, curses in self.all_curses.items():
                if curses:
                    print(f"\n{curse_type}: {len(curses)}")
                    for i, curse in enumerate(curses, 1):
                        severity_emoji = {
                            "high": "🔴",
                            "medium": "🟡",
                            "low": "🟢"
                        }.get(curse.severity, "⚪")
                        print(f"  {i}. {severity_emoji} {curse.curse_name}")
            
            print("\n" + "=" * 60)
            print("⚠️  IMPORTANT RECOMMENDATIONS:")
            print("=" * 60)
            
            # Collect all unique remedies
            all_remedies = set()
            for curses in self.all_curses.values():
                for curse in curses:
                    if curse.remedies:
                        all_remedies.update(curse.remedies)
            
            if all_remedies:
                print("\nSuggested Remedial Measures:")
                for i, remedy in enumerate(sorted(all_remedies), 1):
                    print(f"  {i}. {remedy}")
            
            print("\n💡 Additional Recommendations:")
            print("  - Consult with an experienced Vedic astrologer")
            print("  - Seek guidance from spiritual teachers/gurus")
            print("  - Perform appropriate pujas and rituals")
            print("  - Focus on dharmic duties and positive karma")
            print("  - Maintain regular spiritual practices")
