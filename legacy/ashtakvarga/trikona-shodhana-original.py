"""
Flexible Bhinnashtakvarga Reduction Script
------------------------------------------
Performs:
  1️⃣ Trikona Śodhana (1st reduction)
  2️⃣ Ekādhipati Śodhana (2nd reduction)

You can choose to run both, or only the second, using the RUN_TRIKONA and RUN_EKADHIPATI flags.
"""

from copy import deepcopy

# ----- CONFIGURATION -----

RUN_TRIKONA = True        # Set False to skip Trikona reduction
RUN_EKADHIPATI = True     # Set False to skip Ekadhipati reduction

# Example Bhinnashtakvarga input
# Bhinnashtakvarga input per planet
bv_input_per_planet = {
    "SAV": """
        1-26
        2-35
        3-30
        4-30
        5-31
        6-33
        7-30
        8-22
        9-32
        10-18
        11-24
        12-26
    """,
    "SU": """
        1-6
        2-6
        3-5
        4-3
        5-4
        6-7
        7-3
        8-2
        9-5
        10-0
        11-3
        12-4
    """,
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
    3: "RA",
    4: "MO",
    5: "SA",
    6: "MA",
    7: "VE, ME",
    8: "SU",
    9: "JU, KE",
}

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


# ----- MAIN -----

def main():
    points_per_planet = {planet: parse_bv_points(s) for planet, s in bv_input_per_planet.items()}

    for planet_code, points in points_per_planet.items():
        # Correct: use already parsed points
        planets = parse_planet_positions(planet_positions_raw)

        print_points(f"Input Bhinnashtakvarga Points for {planet_code}", points)

        current_points = points

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

        print("\n" * 2)
        print("===" * 50)
        print("\n" * 2)


# Calculate Nakshatra Ayu Based on Bhinnashtakvarga


if __name__ == "__main__":
    main()
