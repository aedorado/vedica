from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
import json
from .common import SignDetail, DegreesIn, Lord

# --- Model Classes ---

@dataclass
class SwissEphemeris:
    Longitude: float
    Latitude: float
    DistanceAU: float
    SpeedLongitude: float
    SpeedLatitude: float
    SpeedDistance: float

@dataclass
class PlanetDetails:
    # Boolean flags
    IsPlanetAfflicted: bool = False
    IsPlanetAspectedByBeneficPlanets: bool = False
    IsPlanetAspectedByEnemyPlanets: bool = False
    IsPlanetAspectedByFriendPlanets: bool = False
    IsPlanetAspectedByMaleficPlanets: bool = False
    IsPlanetBenefic: bool = False
    IsPlanetBeneficToLagna: bool = False
    IsPlanetCombust: bool = False
    IsPlanetConjunctWithBeneficPlanets: bool = False
    IsPlanetConjunctWithEnemyPlanets: bool = False
    IsPlanetConjunctWithFriendPlanets: bool = False
    IsPlanetConjunctWithMaleficPlanets: bool = False
    IsPlanetDebilitated: bool = False
    IsPlanetExaltedDegree: bool = False
    IsPlanetExaltedSign: bool = False
    IsPlanetFortified: bool = False
    IsPlanetInEnemyHouse: bool = False
    IsPlanetInEnemySign: bool = False
    IsPlanetInFriendHouse: bool = False
    IsPlanetInFriendSign: bool = False
    IsPlanetInGarvitaAvasta: bool = False
    IsPlanetInKendra: bool = False
    IsPlanetInKshobhitaAvasta: bool = False
    IsPlanetInKshuditaAvasta: bool = False
    IsPlanetInLajjitaAvasta: bool = False
    IsPlanetInMoolatrikona: bool = False
    IsPlanetInMuditaAvasta: bool = False
    IsPlanetInOwnHouse: bool = False
    IsPlanetInOwnSign: bool = False
    IsPlanetInTrashitaAvasta: bool = False
    IsPlanetInTrikona: bool = False
    IsPlanetInUpachaya: bool = False
    IsPlanetInWaterySign: bool = False
    IsPlanetMalefic: bool = False
    IsPlanetMaleficToLagna: bool = False
    IsPlanetMarakaToLagna: bool = False
    IsPlanetRetrograde: bool = False
    IsPlanetStrongInShadbala: bool = False
    IsPlanetYogakarakaToLagna: bool = False
    
    # Lists
    AllMaleficPlanetsAspecting: List[str] = field(default_factory=list)
    PlanetTemporaryFriendList: List[str] = field(default_factory=list)
    PlanetsAspectingPlanet: List[str] = field(default_factory=list)
    PlanetsInAspect: List[str] = field(default_factory=list)
    PlanetsInConjunction: List[str] = field(default_factory=list)
    
    # Sign details (nested dictionaries)
    PlanetAkshavedamshaD45Sign: Optional[SignDetail] = None
    PlanetBhamshaD27Sign: Optional[SignDetail] = None
    PlanetChaturthamshaD4Sign: Optional[SignDetail] = None
    PlanetChaturvimshamshaD24Sign: Optional[SignDetail] = None
    PlanetDashamamshaD10Sign: Optional[SignDetail] = None
    PlanetDrekkanaD3Sign: Optional[SignDetail] = None
    PlanetDwadashamshaD12Sign: Optional[SignDetail] = None
    PlanetHoraD2Signs: Optional[SignDetail] = None
    PlanetKhavedamshaD40Sign: Optional[SignDetail] = None
    PlanetNavamshaD9Sign: Optional[SignDetail] = None
    PlanetRasiD1Sign: Optional[SignDetail] = None
    PlanetSaptamshaD7Sign: Optional[SignDetail] = None
    PlanetShashtyamshaD60Sign: Optional[SignDetail] = None
    PlanetShodashamshaD16Sign: Optional[SignDetail] = None
    PlanetTrimshamshaD30Sign: Optional[SignDetail] = None
    PlanetVimshamshaD20Sign: Optional[SignDetail] = None
    PlanetZodiacSignBasedOnHouseLongitudes: Optional[SignDetail] = None
    PlanetEphemerisLongitude: Optional[SignDetail] = None
    PlanetNirayanaLongitude: Optional[SignDetail] = None
    PlanetSayanaLatitude: Optional[SignDetail] = None
    PlanetSayanaLongitude: Optional[SignDetail] = None
    
    # Lord details
    PlanetLordOfConstellation: Optional[Lord] = None
    PlanetLordOfZodiacSign: Optional[Lord] = None
    
    # Numeric values
    PlanetAbdaBala: float = 0.0
    PlanetAyanaBala: float = 0.0
    PlanetDeclination: float = 0.0
    PlanetDigBala: float = 0.0
    PlanetDrekkanaBala: float = 0.0
    PlanetDrikBala: float = 0.0
    PlanetHoraBala: float = 0.0
    PlanetIshtaKashtaScoreDegree: float = 0.0
    PlanetIshtaScore: float = 0.0
    PlanetKalaBala: float = 0.0
    PlanetKashtaScore: float = 0.0
    PlanetKendraBala: float = 0.0
    PlanetMasaBala: float = 0.0
    PlanetNaisargikaBala: float = 0.0
    PlanetNathonnathaBala: float = 0.0
    PlanetNatureScore: float = 0.0
    PlanetOchchaBala: float = 0.0
    PlanetOjayugmarasyamsaBala: float = 0.0
    PlanetOwnAshtakvargaBindu: int = 0
    PlanetPakshaBala: float = 0.0
    PlanetPowerPercentage: float = 0.0
    PlanetSaptavargajaBala: float = 0.0
    PlanetShadbalaPinda: float = 0.0
    PlanetSpeed: float = 0.0
    PlanetSthanaBala: float = 0.0
    PlanetStrength: float = 0.0
    PlanetTribhagaBala: float = 0.0
    PlanetVaraBala: float = 0.0
    ResidentialStrength: float = 0.0
    
    # String values
    HousePlanetOccupiesBasedOnLongitudes: str = ""
    HousePlanetOccupiesBasedOnSign: str = ""
    HousesInAspect: str = ""
    HousesOwnedByPlanet: str = ""
    PlanetAvasta: str = ""
    PlanetConstellation: str = ""
    PlanetDasaEffectsBasedOnIshtaKashta: str = ""
    PlanetDwadashamshaSignOLD: str = ""
    PlanetMotionName: str = ""
    PlanetSaptamshaSignOLD: str = ""
    SignsPlanetIsAspecting: str = ""
    
    # Swiss Ephemeris data
    SwissEphemeris: Optional[Dict[str, float]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlanetDetails':
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

                elif field_name == 'SwissEphemeris' and isinstance(value, dict):
                    kwargs[field_name] = value

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