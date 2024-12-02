# first line: 13
@memory.cache
def geocode_country_cached(country_name):
    geolocator = Nominatim(user_agent="brendabbrios@gmail.com", timeout=10)
    try:
        location = geolocator.geocode(country_name)
        if location:
            return location.latitude, location.longitude
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"Error geocodificando {country_name}: {e}")
    return None, None
