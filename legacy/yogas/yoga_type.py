from enum import Enum

class YogaType(Enum):
    """Enumeration of different types of yoga formations."""
    CONJUNCTION = "Conjunction"
    MUTUAL_ASPECT = "Mutual Aspect"
    ASPECT = "Aspect"  # One-way
    SIGN_EXCHANGE = "Sign Exchange"
    HOUSE_PLACEMENT = "House Placement"
    BENEFIC_PLACEMENT = "Benefic Placement"
    MAHAPURUSH = "Panch Mahapurush Yoga"
    HARSH_YOGA = "Harsha Yoga - 6th lord in 8th or 12th house"
    SARALA_YOGA = "Sarala Yoga - 8th lord in 6th or 12th housea"
    VIMALA_YOGA = "Vimala Yoga - 12th lord in 6th or 8th house"
    MALAVYA_YOGA = "Malavya Yoga - Venus in Kendra in own house or exalted"
    RUCHAKA_YOGA = "Ruchaka Yoga - Mars in Kendra in own house or exalted"
    SASHA_YOGA = "Sasha Yoga - Saturn in Kendra in own house or exalted"
    HAMSA_YOGA = "Hamsa Yoga - Jupiter in Kendra in own house or exalted"
    BHADRA_YOGA = "Bhadra Yoga - Mercury in Kendra in own house or exalted"

    @staticmethod
    def get_pancha_mahapurush_yoga_type(planet: str) -> "YogaType | None":
        """Returns the specific Mahapurush Yoga type for a planet."""
        planet = planet.strip().lower()
        match planet:
            case "mars":
                return YogaType.RUCHAKA_YOGA
            case "mercury":
                return YogaType.BHADRA_YOGA
            case "jupiter":
                return YogaType.HAMSA_YOGA
            case "venus":
                return YogaType.MALAVYA_YOGA
            case "saturn":
                return YogaType.SASHA_YOGA
            case _:
                return None

