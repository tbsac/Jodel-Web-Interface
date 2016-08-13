"""

Utility scripts for resolving locations

"""

import time
import random

random.seed(time.time())

def _find_cache_entry(city, country):
    # TODO: Right now this is hardcoded to Aachen, DE
    return 50.776351, 6.0838618

def _randomize_location(lat, lng):
    return (lat + (random.random() * 2.0 - 1.0) * 0.005,
            lng + (random.random() * 2.0 - 1.0) * 0.005)

def resolve_location(city, country):
    lat, lng = _find_cache_entry(city, country)
    lat, lng = _randomize_location(lat, lng)

    return {
        'country': 'DE',
        'loc_accuracy': 100,
        'loc_coordinates': {
                'lat': str(lat), 'lng': str(lng),
        },
        'city': city
    }
