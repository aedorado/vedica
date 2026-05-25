"""
Curses Detection Module.

Detects various types of curses in astrological charts including:
- Curses from sages (9 conditions)
- Curses from brothers (5 conditions)
- Curses affecting spouse/wife (6 conditions)
- Curses from snakes/nagas (3 conditions)
- Curses from father (5 conditions)
- Curses from mother (8 conditions)
- Curses from spiritual persons/saints (7 conditions)
- Curses from evil spirits/demons (6 conditions)
"""

from .curse_detector import CurseDetector
from .sage_curse_detector import SageCurseDetector
from .brother_curse_detector import BrotherCurseDetector
from .spouse_curse_detector import SpouseCurseDetector
from .snake_curse_detector import SnakeCurseDetector
from .father_curse_detector import FatherCurseDetector
from .mother_curse_detector import MotherCurseDetector
from .spiritual_curse_detector import SpiritualCurseDetector
from .evil_spirit_curse_detector import EvilSpiritCurseDetector
from .curse_detector_base import CurseDetectorBase, CurseRecord

__all__ = [
    "CurseDetector",
    "SageCurseDetector",
    "BrotherCurseDetector",
    "SpouseCurseDetector",
    "SnakeCurseDetector",
    "FatherCurseDetector",
    "MotherCurseDetector",
    "SpiritualCurseDetector",
    "EvilSpiritCurseDetector",
    "CurseDetectorBase",
    "CurseRecord"
]
