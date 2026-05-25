from vedastro import PlanetName, HouseName, Calculate
import time

Calculate.SetAPIKey('FreeAPIUser')
# Fields that must be present and valid (not error strings) for data to be trusted
_REQUIRED_PLANET_FIELDS = ['PlanetNirayanaLongitude', 'PlanetRasiD1Sign', 'PlanetNavamshaD9Sign']
_ERROR_MARKER = 'System.Reflection.TargetInvocationException'


def _validate_planet_data(name: str, data: dict) -> None:
    """Raise ValueError if the planet data dict contains errors in core fields."""
    if not isinstance(data, dict):
        raise ValueError(f"{name}: data is not a dict (got {type(data).__name__})")
    for field in _REQUIRED_PLANET_FIELDS:
        value = data.get(field)
        if value is None:
            raise ValueError(f"{name}: required field '{field}' is missing")
        # Error strings from VedAstro look like stack traces
        if isinstance(value, str) and _ERROR_MARKER in value:
            raise ValueError(f"{name}: field '{field}' contains a VedAstro error:\n{value[:200]}")


def _clean_error_fields(data: dict) -> dict:
    """Replace any field value that is a VedAstro error string with None."""
    return {
        k: (None if isinstance(v, str) and _ERROR_MARKER in v else v)
        for k, v in data.items()
    }


def _validate_all_planets_unique(all_planet_data: dict) -> None:
    """Raise ValueError if all planets share the same NirayanaLongitude (duplicate-Sun bug)."""
    longitudes = set()
    for name, data in all_planet_data.items():
        if isinstance(data, dict):
            lon = data.get('PlanetNirayanaLongitude', {})
            if isinstance(lon, dict):
                longitudes.add(lon.get('TotalDegrees'))
    if len(longitudes) == 1 and len(all_planet_data) > 1:
        raise ValueError(
            f"All {len(all_planet_data)} planets have identical NirayanaLongitude "
            f"({next(iter(longitudes))}°) — VedAstro returned duplicated Sun data. "
            "Aborting to prevent storing corrupted data."
        )


def get_all_planetary_data(birth_time):
    print("🪐 Starting planetary data retrieval...")
    planets = {
        'Sun': PlanetName.Sun, 'Moon': PlanetName.Moon, 'Mars': PlanetName.Mars,
        'Mercury': PlanetName.Mercury, 'Jupiter': PlanetName.Jupiter,
        'Venus': PlanetName.Venus, 'Saturn': PlanetName.Saturn,
        'Rahu': PlanetName.Rahu, 'Ketu': PlanetName.Ketu,
    }

    all_planet_data = {}
    for name, enum in planets.items():
        print(f"🔍 Fetching data for planet: {name}...")
        data = Calculate.AllPlanetData(enum, birth_time)
        if data is None:
            raise ValueError(f"{name}: Calculate.AllPlanetData returned None")
        print(f"{name} Data - {data}\n\n")
        _validate_planet_data(name, data)
        all_planet_data[name] = _clean_error_fields(data)
        print(f"✅ {name} data retrieved.")
        time.sleep(30)

    _validate_all_planets_unique(all_planet_data)
    print("✅ Planetary data retrieval complete.\n")
    return all_planet_data

def get_all_house_data(birth_time):
    print("🏠 Starting house data retrieval...")
    houses = {}
    for i in range(1, 13):
        print(f"🔍 Fetching data for House {i}...")
        time.sleep(30)
        house_enum = getattr(HouseName, f'House{i}')
        data = Calculate.AllHouseData(house_enum, birth_time)
        if data is None:
            raise ValueError(f"House {i}: Calculate.AllHouseData returned None")
        houses[i] = data
        print(f"✅ House {i} data retrieved.")
    print("✅ House data retrieval complete.\n")
    return houses
