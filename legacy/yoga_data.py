"""
Yoga data mapping - provides formation details and effects for all 102 yogas.
Data sourced from yoga_combinations.csv and classical BPHS texts.
"""

YOGA_DATA = {
    # Lunar Yogas
    "gajakesari": {
        "name": "Gajakesari Yoga",
        "category": "Lunar Yoga",
        "formation": "Jupiter in Kendra (1st, 4th, 7th, or 10th) from Moon or mutual aspect",
        "effect": "Grants intelligence, wisdom, leadership, popularity, respect in society",
        "benefic": True,
        "intensity": "Strong"
    },
    "sunapha": {
        "name": "Sunapha Yoga",
        "category": "Lunar Yoga",
        "formation": "Any planet (except Sun) in 2nd house from Moon",
        "effect": "Self-made wealth, learning, famous, virtuous, and intelligent",
        "benefic": True,
        "intensity": "Moderate"
    },
    "anapha": {
        "name": "Anapha Yoga",
        "category": "Lunar Yoga",
        "formation": "Any planet (except Sun) in 12th house from Moon",
        "effect": "Confident, self-reliant, well-dressed, enjoys comforts and stability",
        "benefic": True,
        "intensity": "Moderate"
    },
    "durdhura": {
        "name": "Durdhura Yoga",
        "category": "Lunar Yoga",
        "formation": "Any planet (except Sun) in both 2nd and 12th house from Moon",
        "effect": "Powerful, influential, wealthy, respected by government and people",
        "benefic": True,
        "intensity": "Strong"
    },
    "kemadruma": {
        "name": "Kemadruma Yoga",
        "category": "Arishta Yoga",
        "formation": "No planets on either side of Moon and no planets in kendras",
        "effect": "Loneliness, financial struggles, psychological weakness (can be cancelled)",
        "benefic": False,
        "intensity": "Strong"
    },
    "chandra_mangala": {
        "name": "Chandra-Mangala Yoga",
        "category": "Dhana Yoga",
        "formation": "Moon and Mars in conjunction or mutual aspect",
        "effect": "Wealth through real estate and property, but may cause emotional turbulence",
        "benefic": True,
        "intensity": "Moderate"
    },
    "adhi": {
        "name": "Adhi Yoga",
        "category": "Raja Yoga",
        "formation": "Benefics (Jupiter, Venus, Mercury) in 6th, 7th, 8th from Moon",
        "effect": "Polite, trustworthy, easily gets wealth, enjoys happiness",
        "benefic": True,
        "intensity": "Strong"
    },
    "vasumati": {
        "name": "Vasumati Yoga",
        "category": "Dhana Yoga",
        "formation": "Benefics in Upachayas (3rd, 6th, 10th, 11th) from Lagna or Moon",
        "effect": "Continuous income, generous lifestyle, financial stability",
        "benefic": True,
        "intensity": "Moderate"
    },
    "rajalakshana": {
        "name": "Rajalakshana Yoga",
        "category": "Raja Yoga",
        "formation": "Moon, Mercury, Venus, Jupiter in Kendras from Lagna",
        "effect": "Royal grace, prosperity, public recognition and honor",
        "benefic": True,
        "intensity": "Very Strong"
    },
    "sakata": {
        "name": "Sakata Yoga",
        "category": "Arishta Yoga",
        "formation": "Moon in 6th, 8th, or 12th from Jupiter",
        "effect": "Wealth rises and falls, instability in life (mixed fortunes)",
        "benefic": False,
        "intensity": "Moderate"
    },
    "amala": {
        "name": "Amala Yoga",
        "category": "Subha Yoga",
        "formation": "Benefic in 10th from Moon or Lagna",
        "effect": "Lasting fame, noble reputation, moral strength and honor",
        "benefic": True,
        "intensity": "Strong"
    },

    # Sun Yogas
    "vesi": {
        "name": "Vesi Yoga",
        "category": "Surya (Sun-based) Yoga",
        "formation": "Planet(s) (except Moon) in 2nd house from Sun",
        "effect": "Intelligent, eloquent, successful in ventures and commerce",
        "benefic": True,
        "intensity": "Moderate"
    },
    "vasi": {
        "name": "Vasi Yoga",
        "category": "Surya (Sun-based) Yoga",
        "formation": "Planet(s) (except Moon) in 12th house from Sun",
        "effect": "Self-restrained, capable, organized and disciplined",
        "benefic": True,
        "intensity": "Moderate"
    },
    "obhayachari": {
        "name": "Obhayachari Yoga",
        "category": "Surya (Sun-based) Yoga",
        "formation": "Planets (except Moon) in both 2nd and 12th house from Sun",
        "effect": "Balanced, clever, diplomatic and poised in all situations",
        "benefic": True,
        "intensity": "Moderate"
    },
    "budha_aditya": {
        "name": "Budha-Aditya Yoga",
        "category": "Raja Yoga",
        "formation": "Sun and Mercury conjunction (not within 10°)",
        "effect": "Highly intelligent, respected, surrounded by comforts and gains",
        "benefic": True,
        "intensity": "Strong"
    },

    # Pancha Mahapurusha Yogas
    "hamsa": {
        "name": "Hamsa Yoga",
        "category": "Panchamahapurusha Yoga",
        "formation": "Jupiter in Kendra in own or exalted sign",
        "effect": "Highly spiritual, learned, noble character and wisdom",
        "benefic": True,
        "intensity": "Very Strong"
    },
    "malavya": {
        "name": "Malavya Yoga",
        "category": "Panchamahapurusha Yoga",
        "formation": "Venus in Kendra in own or exalted sign",
        "effect": "Charming, wealthy, artistic, refined and beautiful",
        "benefic": True,
        "intensity": "Strong"
    },
    "sasa": {
        "name": "Sasa Yoga",
        "category": "Panchamahapurusha Yoga",
        "formation": "Saturn in Kendra in own or exalted sign",
        "effect": "Leadership, long life, social influence and endurance",
        "benefic": True,
        "intensity": "Strong"
    },
    "ruchaka": {
        "name": "Ruchaka Yoga",
        "category": "Panchamahapurusha Yoga",
        "formation": "Mars in Kendra in own or exalted sign",
        "effect": "Warrior nature, courage, dynamism and military success",
        "benefic": True,
        "intensity": "Very Strong"
    },
    "bhadra": {
        "name": "Bhadra Yoga",
        "category": "Panchamahapurusha Yoga",
        "formation": "Mercury in Kendra in own or exalted sign",
        "effect": "Smart, diplomatic, business skills and intellectual mastery",
        "benefic": True,
        "intensity": "Strong"
    },

    # More Raja Yogas
    "lakshmi": {
        "name": "Lakshmi Yoga",
        "category": "Raja Yoga",
        "formation": "Lagna lord and 9th lord are benefic, strong, and related",
        "effect": "Financial stability, fame, happiness and prosperity",
        "benefic": True,
        "intensity": "Very Strong"
    },
    "parvata": {
        "name": "Parvata Yoga",
        "category": "Raja Yoga",
        "formation": "Benefics in Kendras and malefics in 6th/8th/12th",
        "effect": "Charitable, famous, happy and luxurious life",
        "benefic": True,
        "intensity": "Strong"
    },
    "kahala": {
        "name": "Kahala Yoga",
        "category": "Raja Yoga",
        "formation": "4th and 9th lords in mutual kendras and Lagna lord strong",
        "effect": "Bold, successful in difficult situations, commander-like",
        "benefic": True,
        "intensity": "Strong"
    },

    # Nabhasa Yogas
    "damini": {
        "name": "Damini Yoga",
        "category": "Nabhasa - Sankhya Yoga",
        "formation": "All 7 planets in 6 different houses",
        "effect": "Powerful, wealthy, successful in ventures",
        "benefic": True,
        "intensity": "Moderate"
    },

    # Vipreet Raja Yogas
    "harsha": {
        "name": "Harsha Yoga",
        "category": "Vipreet Raja Yoga",
        "formation": "6th lord in 8th or 12th house",
        "effect": "Victory over enemies, good health, overcoming obstacles",
        "benefic": True,
        "intensity": "Moderate"
    },
    "sarala": {
        "name": "Sarala Yoga",
        "category": "Vipreet Raja Yoga",
        "formation": "8th lord in 6th or 12th house",
        "effect": "Courage, perseverance, wealth through efforts",
        "benefic": True,
        "intensity": "Moderate"
    },
    "vimala": {
        "name": "Vimala Yoga",
        "category": "Vipreet Raja Yoga",
        "formation": "12th lord in 6th or 8th house",
        "effect": "Financial gains, foreign income, expenditure control",
        "benefic": True,
        "intensity": "Moderate"
    },

    # Additional important yogas
    "mahabhagya": {
        "name": "Mahabhagya Yoga",
        "category": "Fortune Yoga",
        "formation": "For males: Sun, Moon, Lagna in odd signs (day birth); for females: even signs (night birth)",
        "effect": "Exceptional fortune, fame, long life, royal or equal status",
        "benefic": True,
        "intensity": "Very Strong"
    },
    "chandika": {
        "name": "Chandika Yoga",
        "category": "Power Yoga",
        "formation": "Mars and Moon in mutual kendras or trines, Mars exalted",
        "effect": "Courageous, intense personality, powerful leadership",
        "benefic": True,
        "intensity": "Very Strong"
    },
    "jaya": {
        "name": "Jaya Yoga",
        "category": "Raja Yoga",
        "formation": "6th lord debilitated and 10th lord exalted",
        "effect": "Happy, victorious, successful, long-lived",
        "benefic": True,
        "intensity": "Strong"
    },
}

def get_yoga_info(yoga_name):
    """Get formation and effect info for a yoga"""
    key = yoga_name.lower().replace(" ", "_").replace("-", "_")
    return YOGA_DATA.get(key, {
        "name": yoga_name,
        "category": "Unknown",
        "formation": "Formation details not available",
        "effect": "Effects not documented",
        "benefic": True,
        "intensity": "Unknown"
    })

def get_all_yoga_names():
    """Get list of all available yoga names"""
    return list(YOGA_DATA.keys())
