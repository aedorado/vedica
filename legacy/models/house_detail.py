from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import json
from .common import SignDetail, DegreesIn, Lord

@dataclass
class HouseLongitude:
    Begin: float
    Middle: float
    End: float

@dataclass
class HouseDetail:
    # Sign details
    HouseAkshavedamshaD45Sign: Optional[SignDetail] = None
    HouseBhamshaD27Sign: Optional[SignDetail] = None
    HouseBhavaChalitSign: Optional[SignDetail] = None
    HouseChaturthamshaD4Sign: Optional[SignDetail] = None
    HouseChaturvimshamshaD24Sign: Optional[SignDetail] = None
    HouseDashamamshaD10Sign: Optional[SignDetail] = None
    HouseDrekkanaD3Sign: Optional[SignDetail] = None
    HouseDwadashamshaD12Sign: Optional[SignDetail] = None
    HouseHoraD2Sign: Optional[SignDetail] = None
    HouseKhavedamshaD40Sign: Optional[SignDetail] = None
    HouseNavamshaD9Sign: Optional[SignDetail] = None
    HouseRasiSign: Optional[SignDetail] = None
    HouseSaptamshaD7Sign: Optional[SignDetail] = None
    HouseShashtyamshaD60Sign: Optional[SignDetail] = None
    HouseShodashamshaD16Sign: Optional[SignDetail] = None
    HouseTrimshamshaD30Sign: Optional[SignDetail] = None
    HouseVimshamshaD20Sign: Optional[SignDetail] = None
    
    # Lord details
    HouseConstellationLord: Optional[Lord] = None
    LordOfHouse: Optional[Lord] = None
    
    # Lists
    PlanetsAspectingHouse: List[str] = field(default_factory=list)
    PlanetsInHouse: List[str] = field(default_factory=list)
    PlanetsInHouseBasedOnSign: List[str] = field(default_factory=list)
    
    # Boolean flags
    IsBeneficPlanetAspectHouse: bool = False
    IsBeneficPlanetInHouse: bool = False
    IsMaleficPlanetAspectHouse: bool = False
    IsMaleficPlanetInHouse: bool = False
    
    # String values
    HouseConstellation: str = ""
    HouseSignName: str = ""
    HouseStrengthCategory: str = ""
    
    # Numeric values
    HouseNatureScore: float = 0.0
    HouseStrength: float = 0.0
    
    # Special longitude handling
    HouseLongitude: Optional[str] = None  # Store as string, parse separately if needed

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HouseDetail':
        def parse_bool(val):
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.strip().lower() == 'true'
            return bool(val)

        kwargs = {}

        for field_name, value in data.items():
            if field_name in cls.__dataclass_fields__:
                field_type = cls.__dataclass_fields__[field_name].type

                if field_type == bool:
                    kwargs[field_name] = parse_bool(value)

                elif isinstance(value, dict) and 'Name' in value and 'DegreesIn' in value:
                    kwargs[field_name] = SignDetail(
                        Name=value['Name'],
                        DegreesIn=DegreesIn(**value['DegreesIn'])
                    )

                elif isinstance(value, dict) and 'Name' in value and len(value) == 1:
                    kwargs[field_name] = Lord(Name=value['Name'])

                else:
                    kwargs[field_name] = value

        return cls(**kwargs)

    def safe_get(self, key: str, default=None):
        """Safely get attribute value with default."""
        return getattr(self, key, default)
    
    def safe_get_nested(self, *keys):
        """Safely get nested attribute values."""
        current = self
        for key in keys:
            if current is None:
                return None
            if hasattr(current, key):
                current = getattr(current, key)
            else:
                return None
        return current