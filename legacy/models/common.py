from dataclasses import dataclass, field

@dataclass
class DegreesIn:
    DegreeMinuteSecond: str
    TotalDegrees: str

@dataclass
class SignDetail:
    Name: str
    DegreesIn: DegreesIn

@dataclass
class Lord:
    Name: str