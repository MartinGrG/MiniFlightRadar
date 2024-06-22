from opensky_api import OpenSkyApi
api = OpenSkyApi()
data = api.get_flights_by_aircraft("3c675a", 1517184000, 1517270400)
for flight in data:
    print(flight)