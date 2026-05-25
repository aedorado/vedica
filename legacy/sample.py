from vedastro import *

Calculate.SetAPIKey('FreeAPIUser')

# Birth details
birth = Time("14:30 25/10/1992 +05:30",
             GeoLocation("Mumbai", 72.8777, 19.0760))

sun = Calculate.AllPlanetData(PlanetName.Sun, birth)

print(sun)

# Get the big three
# sun_sign = Calculate.PlanetSignName(PlanetName.Sun, birth)
# moon_sign = Calculate.PlanetSignName(PlanetName.Moon, birth)
ascendant = Calculate.HouseSignName(HouseName.House1, birth)

# print(f"☀️ Sun: {sun_sign}")        # e.g., "Libra"
# print(f"🌙 Moon: {moon_sign}")       # e.g., "Scorpio"
print(f"⬆️ Rising: {ascendant}")     # e.g., "Capricorn"