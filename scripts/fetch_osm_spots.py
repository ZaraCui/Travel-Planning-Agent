import requests
import json
import sys
import os
import time

def get_city_area_id(city_name):
    # Use Nominatim to find the relation ID for the city
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name,
        "format": "json",
        "polygon_geojson": 0,
        "limit": 1
    }
    headers = {'User-Agent': 'TravelPlannerAgent/1.0'}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if not data:
            return None
        
        # OSM ID for area is relation ID + 3600000000
        osm_id = int(data[0]['osm_id'])
        osm_type = data[0]['osm_type']
        
        if osm_type == 'relation':
            return osm_id + 3600000000
        elif osm_type == 'way':
            return osm_id + 2400000000
        return None
    except Exception as e:
        print(f"Error fetching city ID: {e}")
        return None

def fetch_spots(city_name):
    area_id = get_city_area_id(city_name)
    if not area_id:
        print(f"Could not find OSM area for {city_name}")
        return []

    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:25];
    area({area_id})->.searchArea;
    (
      node["tourism"~"attraction|museum|viewpoint|zoo|theme_park|gallery"](area.searchArea);
      way["tourism"~"attraction|museum|viewpoint|zoo|theme_park|gallery"](area.searchArea);
      relation["tourism"~"attraction|museum|viewpoint|zoo|theme_park|gallery"](area.searchArea);
      node["historic"~"monument|memorial|castle|ruins"](area.searchArea);
    );
    out center;
    """
    
    print(f"Fetching data from OpenStreetMap for {city_name}...")
    try:
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()
    except Exception as e:
        print(f"Error querying Overpass API: {e}")
        return []
    
    spots = []
    seen_names = set()
    
    for element in data.get('elements', []):
        tags = element.get('tags', {})
        name = tags.get('name')
        
        # Try english name if local name is missing, or prefer english?
        # Let's stick to 'name' tag first, then 'name:en'
        if not name:
            name = tags.get('name:en')
        
        if not name or name in seen_names:
            continue
            
        seen_names.add(name)
        
        lat = element.get('lat') or element.get('center', {}).get('lat')
        lon = element.get('lon') or element.get('center', {}).get('lon')
        
        if lat is None or lon is None:
            continue
            
        # Infer category
        category = 'sightseeing'
        tourism = tags.get('tourism')
        historic = tags.get('historic')
        
        if tourism == 'museum' or tags.get('museum'):
            category = 'museum'
        elif tourism == 'zoo':
            category = 'outdoor'
        elif tourism == 'theme_park':
            category = 'outdoor'
        elif tourism == 'viewpoint':
            category = 'outdoor'
        elif historic:
            category = 'history'
            
        # Create spot object
        spot = {
            "name": name,
            "category": category,
            "duration_minutes": 60, # default
            "rating": 4.0, # default placeholder
            "lat": lat,
            "lon": lon,
            "description": tags.get('description:en') or tags.get('description') or f"A popular {category} spot in {city_name}."
        }
        spots.append(spot)
        
    # Sort by name
    spots.sort(key=lambda x: x['name'])
    return spots

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_osm_spots.py <city_name>")
        sys.exit(1)
        
    city = sys.argv[1]
    spots = fetch_spots(city)
    
    if spots:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        filename = f"data/spots_{city.lower().replace(' ', '')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(spots, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(spots)} spots to {filename}")
    else:
        print("❌ No spots found.")
