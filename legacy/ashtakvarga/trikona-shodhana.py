"""
Flexible Bhinnashtakvarga Reduction Script
------------------------------------------
Performs:
  1️⃣ Trikona Śodhana (1st reduction)
  2️⃣ Ekādhipati Śodhana (2nd reduction)

You can choose to run both, or only the second, using the RUN_TRIKONA and RUN_EKADHIPATI flags.
"""

from copy import deepcopy
from functools import reduce

# ----- CONFIGURATION -----

RUN_TRIKONA = True        # Set False to skip Trikona reduction
RUN_EKADHIPATI = True     # Set False to skip Ekadhipati reduction

# Example Bhinnashtakvarga input
# Bhinnashtakvarga input per planet
bv_input_per_planet = {
    "SAV": """
        1-24
        2-29
        3-27
        4-26
        5-27
        6-26
        7-29
        8-39
        9-28
        10-32
        11-27
        12-23
    """,
    "SU": """
        1-4
        2-3
        3-4
        4-3
        5-5
        6-5
        7-5
        8-4
        9-4
        10-2
        11-4
        12-5
    """,
    # 4  3  4  3  5  5  5  4  4  2  4  5
    "MO": """
        1-5
        2-5
        3-5
        4-5
        5-3
        6-4
        7-4
        8-2
        9-6
        10-6
        11-3
        12-1
    """,
    "MA": """
        1-4
        2-5
        3-2
        4-2
        5-4
        6-6
        7-2
        8-2
        9-4
        10-1
        11-2
        12-5
    """,
    "ME": """
        1-5
        2-5
        3-4
        4-5
        5-5
        6-4
        7-7
        8-3
        9-5
        10-1
        11-5
        12-4
    """,
    "JU": """
        1-2
        2-3
        3-5
        4-7
        5-5
        6-3
        7-5
        8-5
        9-5
        10-6
        11-4
        12-6
    """,
    "VE": """
        1-2
        2-5
        3-5
        4-5
        5-6
        6-4
        7-6
        8-5
        9-3
        10-2
        11-5
        12-4
    """,
    "SA": """
        1-2
        2-5
        3-4
        4-3
        5-4
        6-5
        7-3
        8-3
        9-4
        10-2
        11-2
        12-2
    """,
    # You can add MA, ME, JU, VE, SA similarly
}


# Example Planet Placements (key = rashi, value = CSV of planets)
# Gemini has Rahu
# Cancer has Moon
# Leo has Saturn
# Virgo has Mars
# Libra has Venus, Mercury
# Scorpio has Sun
# Sagittarius has Jupiter, Ketu
# planet_positions_raw = {
#     3: "RA",
#     4: "MO",
#     5: "SA",
#     6: "MA",
#     7: "VE, ME",
#     8: "SU",
#     9: "JU, KE",
# }
# ----- DATA FOR ASHTAKVARGA CALCULATIONS -----
planet_positions_raw = {
    11: "SA",
    1: "JU",
    2: "RA",
    5: "MA",
    6: "MO",
    8: "ME, VE, KE",
    9: "SU"
}
# planet_positions_raw = {
#     3: "RA",
#     4: "MO",
#     5: "SA",
#     6: "MA",
#     7: "VE, ME",
#     8: "SU",
#     9: "JU, KE",
# }
# planet_positions_raw = {
#     1: "SU",
#     3: "RA",
#     4: "MO",
#     8: "SA",
#     9: "KE",
#     10: "MA, JU",
#     11: "VE",
#     12: "ME",
# }

ASCENDENT = 10  # Cancer

# ----- DATA -----

RASHI_NAMES = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
}

PLANET_OWNERSHIP = {
    "Sun": [5],
    "Moon": [4],
    "Mars": [1, 8],
    "Mercury": [3, 6],
    "Jupiter": [9, 12],
    "Venus": [2, 7],
    "Saturn": [10, 11],
}

IGNORED_PLANETS = {"RA", "KE"}  # Rahu, Ketu ignored

TRIKONA_GROUPS = {
    "Fiery (Aries, Leo, Sagittarius)": [1, 5, 9],
    "Earthy (Taurus, Virgo, Capricorn)": [2, 6, 10],
    "Airy (Gemini, Libra, Aquarius)": [3, 7, 11],
    "Watery (Cancer, Scorpio, Pisces)": [4, 8, 12]
}

# ----- RASI GUNAKARA (constant multipliers) -----
RASI_GUNAKARA = {
    1: 7,   # Aries
    2: 10,  # Taurus
    3: 8,   # Gemini
    4: 4,   # Cancer
    5: 10,  # Leo
    6: 5,   # Virgo
    7: 7,   # Libra
    8: 8,   # Scorpio
    9: 9,   # Sagittarius
    10: 5,  # Capricorn
    11: 11, # Aquarius
    12: 12  # Pisces
}

# ----- GRAHA GUNAKARA (planetary factors) -----
GRAHA_GUNAKARA = {
    "SU": 5,
    "MO": 5,
    "MA": 8,
    "ME": 5,
    "JU": 10,
    "VE": 7,
    "SA": 5
}


# ----- HELPER FUNCTIONS -----

def parse_bv_points(s):
    pts = {}
    for line in s.strip().splitlines():
        if "-" in line:
            r, v = line.strip().split("-")
            pts[int(r.strip())] = int(v.strip())
    for i in range(1, 13):
        pts.setdefault(i, 0)
    return pts

def parse_planet_positions(raw_dict):
    """
    Parse raw planet positions dictionary into structured format.
    
    Sample Input:
        {
            3: "RA",
            4: "MO",
            5: "SA",
            7: "VE, ME",
            9: "JU, KE"
        }
    
    Sample Output:
        {
            3: ["RA"],
            4: ["MO"],
            5: ["SA"],
            7: ["VE", "ME"],
            9: ["JU", "KE"]
        }
    """
    parsed = {}
    for r, val in raw_dict.items():
        planets = [p.strip().upper() for p in val.split(",")] if val else []
        parsed[r] = [p for p in planets if p]
    return parsed

def print_points(title, pts):
    print(title)
    for i in range(1, 13):
        print(f"   {RASHI_NAMES[i]} ({i}) = {pts[i]}")
    print()

# ----- TRIKONA ŚODHANA -----

def trikona_shodhana(points):
    print("\n=== Trikona Śodhana (1st Reduction) ===\n")
    reduced = deepcopy(points)

    for group, rashis in TRIKONA_GROUPS.items():
        vals = [points[r] for r in rashis]
        print(f"→ {group}")
        for r in rashis:
            print(f"   {RASHI_NAMES[r]} ({r}) = {points[r]}")

        if vals.count(0) >= 2:
            print("   Rule 3: Two or more zeros → make all zero")
            for r in rashis:
                reduced[r] = 0

        elif 0 in vals:
            print("   Rule 2: One zero → no reduction")

        elif vals[0] == vals[1] == vals[2]:
            print("   Rule 4: All equal → make all zero")
            for r in rashis:
                reduced[r] = 0

        else:
            lowest = min(vals)
            print(f"   Rule 1: Unequal → subtract lowest ({lowest}) from each")
            for r in rashis:
                reduced[r] = points[r] - lowest
            for r in rashis:
                print(f"      {RASHI_NAMES[r]} ({r}) = {reduced[r]}")
        print()
    print("=== End of Trikona Śodhana ===\n")
    return reduced

# ----- EKĀDHIPATI ŚODHANA -----

def ekadhipati_shodhana(points, planet_positions):
    print("\n=== Ekādhipati Śodhana (2nd Reduction) ===\n")
    reduced = deepcopy(points)

    occupants = {
        r: [p for p in planet_positions.get(r, []) if p not in IGNORED_PLANETS]
        for r in range(1, 13)
    }

    print("Rashi Occupancy (excluding RA/KE):")
    for r in range(1, 13):
        occ = occupants[r]
        print(f"   {RASHI_NAMES[r]} ({r}): {', '.join(occ) if occ else 'None'}")
    print()

    for planet, signs in PLANET_OWNERSHIP.items():
        if len(signs) == 1:
            s = signs[0]
            print(f"→ {planet} owns {RASHI_NAMES[s]} ({s}) → single sign → no reduction.\n")
            continue

        s1, s2 = signs
        v1, v2 = points[s1], points[s2]
        occ1, occ2 = occupants[s1], occupants[s2]

        print(f"→ {planet} owns {RASHI_NAMES[s1]} ({s1}) and {RASHI_NAMES[s2]} ({s2})")
        print(f"   Values: {v1}, {v2}")
        print(f"   Occupancy: {RASHI_NAMES[s1]} = {occ1 or 'None'}, {RASHI_NAMES[s2]} = {occ2 or 'None'}")

        if occ1 and occ2:
            print("   Both occupied → no reduction.\n")
            continue
        if v1 == 0 or v2 == 0:
            print("   One sign has 0 points → no reduction.\n")
            continue

        if occ1 and not occ2:
            print(f"   {RASHI_NAMES[s1]} occupied, {RASHI_NAMES[s2]} not → apply rule 4.")
            if v2 > v1:
                reduced[s2] = v1
                print(f"   Unoccupied ({RASHI_NAMES[s2]}) > occupied ({v2}>{v1}) → set to {v1}")
            else:
                reduced[s2] = 0
                print(f"   Unoccupied ({RASHI_NAMES[s2]}) ≤ occupied → set to 0")
        elif occ2 and not occ1:
            print(f"   {RASHI_NAMES[s2]} occupied, {RASHI_NAMES[s1]} not → apply rule 4.")
            if v1 > v2:
                reduced[s1] = v2
                print(f"   Unoccupied ({RASHI_NAMES[s1]}) > occupied ({v1}>{v2}) → set to {v2}")
            else:
                reduced[s1] = 0
                print(f"   Unoccupied ({RASHI_NAMES[s1]}) ≤ occupied → set to 0")
        else:
            print("   Both unoccupied → apply both-unoccupied rules.")
            if v1 == v2:
                reduced[s1] = reduced[s2] = 0
                print("   Equal → both 0")
            elif v1 > v2:
                reduced[s1] = v2
                print(f"   Unequal → larger ({RASHI_NAMES[s1]}) set to smaller ({v2})")
            else:
                reduced[s2] = v1
                print(f"   Unequal → larger ({RASHI_NAMES[s2]}) set to smaller ({v1})")
        print()
    print("=== End of Ekādhipati Śodhana ===\n")
    return reduced


def print_detailed_shodhya(points_after_ekadhipati, planet_positions, planet_code):
    """
    Prints detailed Rasi Pinda, Graha Pinda, and Shodhya Pinda for each planet.
    Returns a dict with totals: { 'rasi_pinda': X, 'graha_pinda': Y, 'shodhya_pinda': Z }
    """

    # --- Rasi Pinda ---
    print(f"\n=== Rasi Pinda for {planet_code} (bindus × Rasi Gunakara) ===")
    total_rasi_pinda = 0
    for rashi in range(1, 13):
        bindus = points_after_ekadhipati[rashi]
        rasi_mult = RASI_GUNAKARA[rashi]
        product = bindus * rasi_mult
        total_rasi_pinda += product
        # Alignment: rashi number (2 chars), rashi name (12 chars), bindus (3), multiplier (3), product (3)
        print(f"{rashi:2}. {RASHI_NAMES[rashi]:<12} {bindus:<3} X {rasi_mult:<3} = {product:<3}")

    print(f"Total Rasi Pinda = {total_rasi_pinda}\n")

    # --- Graha Pinda ---
    print("=== Graha Pinda (bindus × Graha Gunakara, one line per planet) ===")
    total_graha_pinda = 0
    for planet_code, factor in GRAHA_GUNAKARA.items():
        graha_total = 0
        contributions = []
        for rashi, planets in planet_positions.items():
            if planet_code in planets:
                bindus = points_after_ekadhipati[rashi]
                product = bindus * factor
                graha_total += product
                contributions.append(f"{RASHI_NAMES[rashi]:<11} ({rashi:2}): {bindus:<2} × {factor:<2} = {product:<3}")
        total_graha_pinda += graha_total

        line = "  |  ".join(contributions) if contributions else "No bindus → 0"
        print(f"{planet_code:<3}: {line}  | Total = {graha_total}")

    # --- Shodhya Pinda ---
    total_shodhya = total_rasi_pinda + total_graha_pinda
    print(f"\nRasi Pinda = {total_rasi_pinda}")
    print(f"Graha Pinda = {total_graha_pinda}")
    print(f"Shodhya Pinda (Total) for {planet_code} = {total_shodhya}\n")

    # Return totals in case you want to use them programmatically
    return {
        'rasi_pinda': total_rasi_pinda,
        'graha_pinda': total_graha_pinda,
        'shodhya_pinda': total_shodhya
    }


def calc_nakshatra_ayu_using_sav(after_ekadhipati):
    """
    Calculate Nakshatra Ayu based on SAV Shodhya Pinda.
    
    Formula:
    1. Shodhya Pinda = Graha Pinda + Rasi Pinda
    2. Multiply by 7 and divide by 27 to get quotient
    3. Multiply quotient by 324 and divide by 365 to get Nakshatra Ayu in years
    """
    print("\n=== Nakshatra Ayu Calculation (SAV) ===")
    
    # Calculate Shodhya Pinda components
    totals = print_detailed_shodhya(after_ekadhipati, parse_planet_positions(planet_positions_raw), "SAV")
    shodhya_pinda = totals['shodhya_pinda']
    
    print(f"Shodhya Pinda (SAV) = {shodhya_pinda}")
    
    # Step 1: Multiply by 7 and divide by 27
    step1_result = (shodhya_pinda * 7) / 27
    quotient = int(step1_result)
    print(f"Step 1: {shodhya_pinda} × 7 ÷ 27 = {step1_result:.2f} (Quotient = {quotient})")
    
    # Step 2: Multiply quotient by 324 and divide by 365
    nakshatra_ayu = (quotient * 324) / 365
    nakshatra_ayu_years = int(nakshatra_ayu)
    print(f"Step 2: {quotient} × 324 ÷ 365 = {nakshatra_ayu:.2f}")
    print(f"\n✨ Nakshatra Ayu = {nakshatra_ayu_years} years (approx.)\n")
    
    return nakshatra_ayu_years


# ----- MAIN -----

def calculate_longevity(planet_code, shodhya_pinda):
    # Multiply Shodhya Pinda by 7 and divide by 27
    product = shodhya_pinda * 7
    quotient = round(product / 27.0, 2)
    
    # If quotient > 27, reduce by 27 and take balance
    if quotient > 27:
        balance = quotient % 27
        print(f"Shodhya Pinda = {shodhya_pinda}")
        print(f"{shodhya_pinda} × 7 = {product}")
        print(f"{product} ÷ 27 = {quotient}")
        print(f"Quotient {quotient} > 27, so balance = {quotient} mod 27 = {balance}")
        gross_years = balance
    else:
        gross_years = quotient
        print(f"Shodhya Pinda = {shodhya_pinda}")
        print(f"{shodhya_pinda} × 7 = {product}")
        print(f"{product} ÷ 27 = {gross_years}")
    
    print(f"✨ Gross years of longevity from {planet_code} = {gross_years} years\n")

    print("=== Longevity Reduction Summary ===")
    # FIRST REDUCTION
    # Reduction by one half
    # Implement only point (i) & (ii) for simplicity
    # (i) More than one planet in a rasi — If there are more than one planet in a rasi its
    # term of life should be reduced by one half. Eg. If Venus and Mercury are together in Libra, 
    # so that term for each is reduced by one half.
    # (ii) If a planet is debilitated, one half is be deducted.
    # (iii) If a planet is in combustion, one half is be deducted.

    # SECOND REDUCTION
    # Reduction by one third
    # Implement only point (i) and not (ii) and (iii) for simplicity
    # (i) If a planet is in sign of an enemy. (Eg Saturn is in Leo, Mars in Virgo, etc
    # both in the signs of enemy, hence a reduction of 1/3 has to be made
    # (ii) If a planet suffers defeat in graha Yuddha (planetary war). A planet is Victor if
    # it has less longitude, and there is planetary war if planets are within 1 degree of
    # each other. (According to some astrologers planet with greater longitude is
    # victor) This rule does not apply to Sun and Moon who do not enter into graha
    # yuddha.
    # iii) If Sun and Moon are eclipsed or of unusual appearance.

    # THIRD REDUCTION
    # Reduction in Visible half of Zodiac
    # When planets are placed in visible half (in houses 7 to 12), they are subjected to reduction as follows :
    # Planets In Reduction for Maleflcs
    # Reduction for beneflc planets - for malefic planet - for benefic planet 
    # (eg. in 11th house, for malefic planet reduction is 1/2, for benefic planet reduction is 1/4 etc.) are as follows :
    # (i) the 12th house Full 1/2
    # (ii) the 11th house 1/2 1/4
    # (iii) the 10th house 1/3 1/6
    # (iv) the 9th house 1/4 1/8
    # (v) the 8th house 1/5 1/10
    # (vi) the 7th house 1/6 1/12

    # When same planet is subject to many reductions, only highest reduction should be applied.

    """
    Apply the three reductions for longevity calculation:
    1. First Reduction: Half if multiple planets in sign OR debilitated
    2. Second Reduction: Third if in enemy sign
    3. Third Reduction: Based on visible half (houses 7-12)
    
    Takes highest reduction only when multiple apply.
    """
    
    # Define benefics and malefics
    BENEFICS = {"JU", "VE", "ME", "MO"}  # Mercury is benefic when alone
    MALEFICS = {"SU", "MA", "SA"}
    
    # Enemy relationships (simplified)
    ENEMY_SIGNS = {
        "SU": [2, 7, 10, 11],  # Libra, Aquarius
        "MO": [],  # Capricorn, Aquarius
        "MA": [3, 6],  # Gemini, Virgo
        "ME": [4],  # Cancer
        "JU": [2, 3, 6, 7],  # Gemini, Virgo
        "VE": [4, 5],  # Aries, Scorpio
        "SA": [1, 4, 5, 8],  # Cancer, Leo
    }
    
    # Debilitation signs
    DEBILITATION_SIGNS = {
        "SU": 7,   # Libra
        "MO": 8,   # Scorpio
        "MA": 4,   # Cancer
        "ME": 12,  # Pisces
        "JU": 10,  # Capricorn
        "VE": 6,   # Virgo
        "SA": 1,   # Aries
    }
    
    # Visible half reductions (houses 7-12)
    VISIBLE_REDUCTIONS = {
        12: {"malefic": 1.0, "benefic": 0.5},
        11: {"malefic": 0.5, "benefic": 0.25},
        10: {"malefic": 1/3, "benefic": 1/6},
        9: {"malefic": 0.25, "benefic": 0.125},
        8: {"malefic": 0.2, "benefic": 0.1},
        7: {"malefic": 1/6, "benefic": 1/12},
    }
    
    planets = parse_planet_positions(planet_positions_raw)
    
    print("\n=== Longevity Reductions ===")
    
    # Count planets per sign (excluding nodes)
    sign_occupancy = {}
    for rashi in range(1, 13):
        sign_occupancy[rashi] = [p for p in planets.get(rashi, []) if p not in IGNORED_PLANETS]
    
    # Find which rashi this planet is in
    planet_rashi = None
    for rashi, occupants in sign_occupancy.items():
        if planet_code in occupants:
            planet_rashi = rashi
            break
    
    if planet_rashi is None:
        print(f"⚠️  {planet_code}: Not found in chart - no reductions applied")
        return gross_years
    
    print(f"\n📍 Analyzing {planet_code} in {RASHI_NAMES[planet_rashi]} (House {planet_rashi})")
    print(f"   Co-occupants: {', '.join(sign_occupancy[planet_rashi]) if len(sign_occupancy[planet_rashi]) > 1 else 'None'}")
    print(f"   Gross years before reduction: {gross_years}")
    
    reductions = []
    
    # FIRST REDUCTION: Multiple planets or debilitation
    print("\n🔍 Checking First Reduction (Half if multiple planets or debilitated):")
    if len(sign_occupancy[planet_rashi]) > 1:
        reductions.append(("Multiple planets in sign", 0.5))
        print(f"   ✓ Multiple planets in {RASHI_NAMES[planet_rashi]}: Reduction = 50%")
    else:
        print(f"   ✗ Single planet in sign: No reduction")
    
    if DEBILITATION_SIGNS.get(planet_code) == planet_rashi:
        reductions.append(("Debilitated", 0.5))
        print(f"   ✓ {planet_code} debilitated in {RASHI_NAMES[planet_rashi]}: Reduction = 50%")
    else:
        debil_sign = DEBILITATION_SIGNS.get(planet_code)
        debil_name = RASHI_NAMES[debil_sign] if debil_sign else "N/A"
        print(f"   ✗ Not debilitated (debilitation sign: {debil_name}): No reduction")
    
    # SECOND REDUCTION: Enemy sign
    print("\n🔍 Checking Second Reduction (Third if in enemy sign):")
    if planet_rashi in ENEMY_SIGNS.get(planet_code, []):
        reductions.append(("Enemy sign", 1/3))
        print(f"   ✓ {planet_code} in enemy sign {RASHI_NAMES[planet_rashi]}: Reduction = 33.33%")
    else:
        enemy_signs = [RASHI_NAMES[s] for s in ENEMY_SIGNS.get(planet_code, [])]
        print(f"   ✗ Not in enemy sign (enemy signs: {', '.join(enemy_signs) if enemy_signs else 'None'}): No reduction")
    
    # THIRD REDUCTION: Visible half (houses 7-12)
    print("\n🔍 Checking Third Reduction (Visible half - houses 7-12):")
    # Calculate house from rashi using ascendant
    planet_house = ((planet_rashi - ASCENDENT) % 12) + 1
    print(f"   Planet house (from ascendant {RASHI_NAMES[ASCENDENT]}): {planet_house}")
    
    if planet_house in VISIBLE_REDUCTIONS:
        is_benefic = planet_code in BENEFICS
        planet_type = "benefic" if is_benefic else "malefic"
        reduction_fraction = VISIBLE_REDUCTIONS[planet_house][planet_type]
        reductions.append((f"Visible half (house {planet_house})", reduction_fraction))
        print(f"   ✓ {planet_code} ({planet_type}) in visible half (house {planet_house}): Reduction = {reduction_fraction:.2%}")
    else:
        print(f"   ✗ Not in visible half (houses 7-12): No reduction")
    
    # Apply only highest reduction
    print("\n📊 Summary of Applicable Reductions:")
    if reductions:
        for reason, fraction in reductions:
            print(f"   • {reason}: -{fraction:.2%}")
        
        max_reduction = max(reductions, key=lambda x: x[1])
        reduction_factor = 1 - max_reduction[1]
        print(f"\n🎯 Applying HIGHEST reduction only:")
        print(f"   Reason: {max_reduction[0]}")
        print(f"   Reduction: -{max_reduction[1]:.2%}")
        print(f"   Multiplier: {reduction_factor:.2%}")
        
        longevity_years = gross_years * reduction_factor
        print(f"\n✨ Calculation: {gross_years} years × {reduction_factor:.2%} = {longevity_years:.2f} years")
        print(f"   Net longevity from {planet_code} = {longevity_years:.2f} years\n")
        return longevity_years
    else:
        print("   No reductions applicable")
        print(f"\n✨ Net longevity from {planet_code} = {gross_years} years (unchanged)\n")
        return gross_years


def main():
    points_per_planet = {planet: parse_bv_points(s) for planet, s in bv_input_per_planet.items()}

    for planet_code, points in points_per_planet.items():
        # Correct: use already parsed points
        planets = parse_planet_positions(planet_positions_raw)

        print_points(f"Input Bhinnashtakvarga Points for {planet_code}", points)

        current_points = points

        # Special handling for SAV: divide by 12 with remainder rule
        if planet_code == "SAV":
            print("\n=== Special SAV Processing: Divide by 12 (remainder never 0) ===")
            sav_reduced = {}
            for rashi in range(1, 13):
                original = current_points[rashi]
                remainder = original % 12
                if remainder == 0:
                    remainder = 12
                sav_reduced[rashi] = remainder
                print(f"   {RASHI_NAMES[rashi]} ({rashi}): {original} → {original} mod 12 = {remainder}")
            current_points = sav_reduced
            print_points(f"After SAV Division by 12 for {planet_code}", current_points)
            print()

        if RUN_TRIKONA:
            current_points = trikona_shodhana(current_points)
            print_points(f"After Trikona Śodhana for {planet_code}", current_points)
        else:
            print("Skipping Trikona Śodhana as per user choice.\n")

        if RUN_EKADHIPATI:
            after_ekadhipati = ekadhipati_shodhana(current_points, planets)
            current_points = after_ekadhipati  # keep current_points updated
            print_points(f"After Ekādhipati Śodhana for {planet_code}", current_points)
        else:
            print("Skipping Ekādhipati Śodhana as per user choice.\n")
            after_ekadhipati = current_points  # in case we skip, use current points

        print("=== Final Results ===")
        for i in range(1, 13):
            print(f"{RASHI_NAMES[i]} ({i}) = {current_points[i]}")

        # Print Shodhya Pinda
        print_detailed_shodhya(after_ekadhipati, planets, planet_code)

        if planet_code == "SAV":
            calc_nakshatra_ayu_using_sav(after_ekadhipati)
        else:
            # Calculate planetary contribution to longevity
            if planet_code != "SAV":
                print(f"\n=== Longevity Contribution from {planet_code} ===")
                totals = print_detailed_shodhya(after_ekadhipati, planets, planet_code)
                shodhya_pinda = totals['shodhya_pinda']

                calculate_longevity(planet_code, shodhya_pinda)


        print("\n" * 2)
        print("===" * 50)
        print("\n" * 2)


# Calculate Nakshatra Ayu Based on Bhinnashtakvarga


if __name__ == "__main__":
    main()
