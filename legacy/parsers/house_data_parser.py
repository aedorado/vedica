from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json
from models.house_detail import DegreesIn, SignDetail, Lord, HouseDetail

class HouseDataParser:
    def __init__(self, json_data: str):
        self.raw_data = json.loads(json_data)

    def _parse_degrees(self, data: dict) -> DegreesIn:
        return DegreesIn(**data)

    def _parse_sign_detail(self, data: dict) -> SignDetail:
        return SignDetail(
            Name=data['Name'], 
            DegreesIn=self._parse_degrees(data['DegreesIn'])
        )

    def _parse_lord(self, data: dict) -> Lord:
        return Lord(**data)

    def _parse_house_detail(self, data: dict) -> HouseDetail:
        kwargs = {}
        
        for field_name, value in data.items():
            if field_name in HouseDetail.__dataclass_fields__:
                # Handle SignDetail objects
                if isinstance(value, dict) and 'Name' in value and 'DegreesIn' in value:
                    kwargs[field_name] = self._parse_sign_detail(value)
                # Handle Lord objects
                elif isinstance(value, dict) and 'Name' in value and len(value) == 1:
                    kwargs[field_name] = self._parse_lord(value)
                # Handle lists and basic types
                else:
                    kwargs[field_name] = value
                    
        return HouseDetail(**kwargs)

    def parse(self) -> Dict[str, HouseDetail]:
        houses = {}
        for house_num, details in self.raw_data.items():
            try:
                houses[house_num] = self._parse_house_detail(details)
            except Exception as e:
                print(f"Error parsing house {house_num}: {e}")
                continue
        return houses