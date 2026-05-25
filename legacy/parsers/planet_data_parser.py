from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
import json
from models.planet_detail import PlanetDetails

class PlanetDataParser:
    def __init__(self, raw: Union[str, Dict[str, Any]]):
        if isinstance(raw, str):
            self.raw = json.loads(raw)
        elif isinstance(raw, dict):
            self.raw = raw
        else:
            raise TypeError("Expected JSON string or dict")

    def parse(self) -> Dict[str, PlanetDetails]:
        planets: Dict[str, PlanetDetails] = {}
        for name, pdata in self.raw.items():
            try:
                planets[name] = PlanetDetails.from_dict(pdata)
            except Exception as e:
                print(f"Error parsing planet {name}: {e}")
                # You might want to handle this differently
                continue
        return planets