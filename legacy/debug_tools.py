def debug_output(planet_data, house_data, path="debug_output.txt"):
    with open(path, "w") as f:
        # Debug output for all planets in sorted order
        for planet in sorted(planet_data.keys()):
            f.write(f"\n=== {planet} Data ===\n")
            for key in sorted(planet_data[planet].keys()):
                f.write(f"\t{key}: {planet_data[planet][key]}\n")

        # Debug output for all 12 houses (1 to 12)
        for house_num in range(1, 13):
            house_key = str(house_num)
            if house_key in house_data:
                f.write(f"\n=== House {house_key} Data ===\n")
                for key in sorted(house_data[house_key].keys()):
                    f.write(f"\t{key}: {house_data[house_key][key]}\n")
