# 🗺️ Open Source Mapping Integration Guide

## Overview

OpenRoute.AI now features a complete **open source mapping stack** with accessibility-first routing and navigation. This implementation uses:

- **OpenStreetMap (OSM)** - Free, community-driven map tiles
- **OpenRouteService API** - Open source routing engine with accessibility support
- **Overpass API** - Real-time OpenStreetMap data queries for accessibility features
- **Leaflet.js** - Open source interactive maps library

## ✨ Key Features

### 🗺️ Interactive Mapping
- OpenStreetMap tiles (100% free, no API key needed for tiles)
- Responsive, mobile-friendly map interface
- Custom markers for different place types
- Popup information with accessibility details

### 🚗 Advanced Routing
- Multi-point route optimization
- Wheelchair-accessible routing (avoids steps, steep inclines)
- Avoid highways/tolls options
- Turn-by-turn directions
- Route distance and duration calculation
- Elevation profile (ascent/descent)

### ♿ Accessibility Integration
- **OpenStreetMap accessibility data integration**
- Wheelchair accessibility information for venues
- Ramp locations
- Elevator availability
- Tactile paving markers
- Accessible toilet information
- Disabled parking spots
- Width measurements for paths

### 🎯 Itinerary Optimization
- Automatic place ordering for minimum travel time/distance
- User preference-based optimization
- Accessibility-aware route planning
- Integration with existing user optimization preferences

---

## 🚀 Getting Started

### 1. Get OpenRouteService API Key (FREE)

1. Visit [https://openrouteservice.org/dev/#/signup](https://openrouteservice.org/dev/#/signup)
2. Create a free account
3. Generate an API key
4. **Free tier includes**: 2,000 requests/day (more than enough for most apps)

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# Mapping and Routing APIs
OPENROUTESERVICE_API_KEY=your-openrouteservice-api-key-here
OVERPASS_API_URL=https://overpass-api.de/api/interpreter
```

The Overpass API (for accessibility data) requires **no API key** and is completely free!

### 3. Install Dependencies

Backend:
```bash
pip install -r requirements.txt
# Installs: openrouteservice==2.3.3, requests==2.32.3
```

Frontend dependencies are already included (Leaflet, React-Leaflet).

### 4. Run Migrations

No new database migrations are needed - the mapping system integrates seamlessly with existing models!

---

## 📚 API Endpoints

### Calculate Route

**Endpoint**: `GET /api/routing/calculate/`

**Description**: Calculate an optimized route between multiple places

**Parameters**:
- `place_ids` (required): Comma-separated list of Place IDs
- `wheelchair_accessible` (optional): Boolean, default: false
- `avoid_highways` (optional): Boolean, default: false
- `avoid_tolls` (optional): Boolean, default: false

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/routing/calculate/?place_ids=1,2,3&wheelchair_accessible=true" \
  -H "Authorization: Token YOUR_TOKEN"
```

**Example Response**:
```json
{
  "route": {
    "distance_meters": 5240,
    "distance_km": 5.24,
    "duration_seconds": 720,
    "duration_minutes": 12.0,
    "ascent_meters": 45,
    "descent_meters": 38,
    "geometry": {
      "type": "LineString",
      "coordinates": [[lon, lat], ...]
    },
    "instructions": [
      {
        "instruction": "Head north on Main St",
        "distance": 150
      }
    ],
    "bbox": [minLon, minLat, maxLon, maxLat]
  },
  "places": [...]
}
```

### Optimize Itinerary

**Endpoint**: `POST /api/routing/optimize-itinerary/`

**Description**: Find optimal order to visit places in an itinerary

**Parameters**:
- `itinerary_id` (required): ID of itinerary to optimize

**Example Response**:
```json
{
  "itinerary_id": 5,
  "optimized_order": [1, 3, 2],
  "total_distance_km": 12.5,
  "total_duration_minutes": 25.5,
  "message": "Apply this new order to your itinerary for optimal routing"
}
```

### Get Accessibility Features Nearby

**Endpoint**: `GET /api/accessibility/nearby/`

**Description**: Find wheelchair accessible venues, ramps, elevators near a location

**Parameters**:
- `latitude` (required): Center point latitude
- `longitude` (required): Center point longitude
- `radius` (optional): Search radius in meters, default: 1000

**Example Response**:
```json
{
  "search_center": {
    "latitude": 51.505,
    "longitude": -0.09
  },
  "radius_meters": 1000,
  "features": {
    "wheelchair_accessible": [...],
    "ramps": [...],
    "elevators": [...],
    "tactile_paving": [...],
    "wide_paths": [...]
  },
  "summary": {
    "wheelchair_accessible_count": 15,
    "ramps_count": 8,
    "elevators_count": 3,
    "tactile_paving_count": 12,
    "wide_paths_count": 20
  }
}
```

### Enrich Place with Accessibility Data

**Endpoint**: `POST /api/accessibility/enrich-place/`

**Description**: Automatically fetch and update a place with OSM accessibility data

**Parameters**:
- `place_id` (required): ID of place to enrich

**Example Response**:
```json
{
  "place_id": 42,
  "name": "Central Library",
  "accessibility_features": "Wheelchair Accessible, Ramp Available, Elevator Available, Accessible Toilets",
  "message": "Place enriched with OpenStreetMap accessibility data"
}
```

---

## 🎨 Frontend Components

### MapView Component

Display an interactive map with places and routes.

```javascript
import MapView from './components/MapView';

<MapView
  places={places}              // Array of place objects
  route={routeData}            // Route geometry from API
  center={[51.505, -0.09]}     // [lat, lng]
  zoom={13}                    // Initial zoom level
  showAccessibilityFeatures={true}
  onPlaceClick={(place) => console.log(place)}
  height="600px"
/>
```

**Props**:
- `places`: Array of place objects with `{id, name, latitude, longitude, place_type, accessibility_features}`
- `route`: Route geometry from OpenRouteService (GeoJSON LineString)
- `center`: Map center as `[latitude, longitude]`
- `zoom`: Initial zoom level (1-19)
- `showAccessibilityFeatures`: Boolean to display accessibility markers
- `onPlaceClick`: Callback function when marker is clicked
- `height`: Map container height (default: '500px')

### RouteDisplay Component

Display route calculation interface and results.

```javascript
import RouteDisplay from './components/RouteDisplay';

<RouteDisplay
  places={selectedPlaces}
  onRouteCalculated={(routeData) => {
    setRoute(routeData);
  }}
  showAccessibilityOptions={true}
/>
```

**Props**:
- `places`: Array of selected places for routing
- `onRouteCalculated`: Callback with route data when calculated
- `showAccessibilityOptions`: Show wheelchair/accessibility preferences (default: true)

---

## 🔧 Backend Services

### RoutingService

```python
from openRoute_app.routing_service import get_routing_service

routing_service = get_routing_service()

# Calculate route
route = routing_service.get_route(
    coordinates=[(lon1, lat1), (lon2, lat2)],
    wheelchair_accessible=True,
    avoid_features=['highways', 'tollways']
)

# Optimize itinerary
optimized = routing_service.optimize_itinerary(
    start_location=(lon, lat),
    destinations=[(lon1, lat1), (lon2, lat2)],
    optimization_preferences={'minimize_travel_time': True}
)

# Get reachability isochrones
isochrones = routing_service.get_isochrones(
    location=(lon, lat),
    range_seconds=[300, 600, 900],  # 5, 10, 15 minutes
    wheelchair_accessible=True
)
```

### OSMAccessibilityService

```python
from openRoute_app.osm_accessibility_service import get_osm_accessibility_service

osm_service = get_osm_accessibility_service()

# Get accessibility features nearby
features = osm_service.get_accessibility_features_nearby(
    latitude=51.505,
    longitude=-0.09,
    radius_meters=1000
)

# Get venue accessibility
accessibility = osm_service.get_venue_accessibility(
    latitude=51.505,
    longitude=-0.09,
    venue_name="Central Library"
)

# Enrich place with OSM data
accessibility_str = osm_service.enrich_place_with_osm_data(
    place_name="Restaurant",
    latitude=51.505,
    longitude=-0.09
)
```

---

## ♿ Accessibility Data from OpenStreetMap

The Overpass API queries OSM for these accessibility tags:

| Feature | OSM Tag | Description |
|---------|---------|-------------|
| Wheelchair Access | `wheelchair=yes` | Venue is wheelchair accessible |
| Ramps | `ramp=yes` | Ramp available |
| Elevators | `highway=elevator` | Elevator locations |
| Tactile Paving | `tactile_paving=yes` | For visually impaired navigation |
| Width | `width >= 1.2m` | Paths wide enough for wheelchairs |
| Accessible Toilets | `toilets:wheelchair=yes` | Wheelchair-accessible restrooms |
| Disabled Parking | `parking:disabled=yes` | Designated accessible parking |
| Automatic Doors | `automatic_door=yes` | Automatic entrance doors |

---

## 💡 Usage Examples

### Example 1: Basic Route Display

```javascript
import React, { useState } from 'react';
import MapView from './components/MapView';
import RouteDisplay from './components/RouteDisplay';

function ItineraryPlanner() {
  const [places, setPlaces] = useState([/* user's places */]);
  const [route, setRoute] = useState(null);

  return (
    <div>
      <RouteDisplay
        places={places}
        onRouteCalculated={(data) => setRoute(data.route)}
      />
      <MapView
        places={places}
        route={route}
        height="600px"
      />
    </div>
  );
}
```

### Example 2: Accessibility-First Navigation

```javascript
function AccessibleRouting() {
  const [wheelchairMode, setWheelchairMode] = useState(true);

  return (
    <RouteDisplay
      places={selectedPlaces}
      onRouteCalculated={(data) => {
        console.log('Wheelchair accessible route:', data);
      }}
      showAccessibilityOptions={true}
    />
  );
}
```

### Example 3: Enrich Places with OSM Data

```python
# In Django view or management command
from openRoute_app.models import Place
from openRoute_app.osm_accessibility_service import get_osm_accessibility_service

osm_service = get_osm_accessibility_service()

for place in Place.objects.filter(accessibility_features__isnull=True):
    accessibility = osm_service.enrich_place_with_osm_data(
        place_name=place.name,
        latitude=float(place.latitude),
        longitude=float(place.longitude)
    )
    place.accessibility_features = accessibility
    place.save()
    print(f"Enriched {place.name}: {accessibility}")
```

---

## 🌍 Why Open Source?

### Cost
- **$0/month** for map tiles (OpenStreetMap)
- **FREE tier** for routing (2,000 requests/day with OpenRouteService)
- **No API key needed** for Overpass API (unlimited use)

### Privacy
- No tracking or analytics from map providers
- Data stays on OpenStreetMap's open platform
- User location data not shared with third parties

### Data Quality
- Community-maintained, constantly improving
- Excellent coverage worldwide
- Rich accessibility tagging by OSM contributors

### Flexibility
- Can self-host OpenRouteService if needed
- Full control over map styling and features
- Can contribute back to OpenStreetMap

---

## 🎯 Best Practices

### 1. Cache Responses
The OSM services automatically cache results using Django's cache framework (Redis recommended).

### 2. Rate Limiting
- OpenRouteService free tier: 2,000 requests/day (40 requests/minute)
- Overpass API: Be respectful, cache aggressively

### 3. Accessibility Data
- Enrich places with OSM data during creation or as a background task
- Don't query for every map view - use cached data
- Update periodically (OSM data changes as community edits)

### 4. Error Handling
- Always check if API keys are configured
- Provide fallback behavior if routing fails
- Show helpful messages to users about API configuration

---

## 🔒 Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Environment Variables**: Store all keys in `.env` file
3. **Rate Limiting**: Implement rate limiting on your API endpoints
4. **User Input Validation**: Validate coordinates and place IDs
5. **CORS**: Configure CORS appropriately for production

---

## 📊 Performance Tips

1. **Use Redis Caching**: Cache Overpass API responses (configured automatically)
2. **Lazy Load Maps**: Only render map when user scrolls to it
3. **Optimize Place Count**: Limit number of markers displayed at once
4. **Debounce API Calls**: Wait for user to finish selecting places
5. **Compress Geometries**: Use simplified route geometries for display

---

## 🐛 Troubleshooting

### "Could not calculate route"
- Check `OPENROUTESERVICE_API_KEY` is set in `.env`
- Verify API key is valid at [https://openrouteservice.org](https://openrouteservice.org)
- Check you haven't exceeded rate limit (2,000 requests/day)

### Map tiles not loading
- Check internet connection
- Try alternative tile provider (see MapView component comments)
- Verify no browser ad-blocker is blocking tiles

### No accessibility data found
- OSM data may not be available for all locations
- Try increasing search radius
- Contribute to OpenStreetMap to improve data!

### API rate limit exceeded
- OpenRouteService: Wait until next day or upgrade plan
- Overpass API: Reduce query frequency, increase caching

---

## 🚀 Future Enhancements

Potential additions to the mapping system:

1. **Offline Maps**: Download map tiles for offline use
2. **Real-time Traffic**: Integrate traffic data into routing
3. **Public Transit**: Add transit routing options
4. **Voice Navigation**: Turn-by-turn audio instructions
5. **AR Navigation**: Augmented reality wayfinding
6. **Community Reports**: User-submitted accessibility updates
7. **Historical Routes**: Save and share favorite routes
8. **Multi-modal**: Combine walking, driving, transit

---

## 📖 Resources

- **OpenStreetMap**: [https://www.openstreetmap.org](https://www.openstreetmap.org)
- **OpenRouteService**: [https://openrouteservice.org](https://openrouteservice.org)
- **Overpass API**: [https://wiki.openstreetmap.org/wiki/Overpass_API](https://wiki.openstreetmap.org/wiki/Overpass_API)
- **Leaflet**: [https://leafletjs.com](https://leafletjs.com)
- **OSM Accessibility Tags**: [https://wiki.openstreetmap.org/wiki/Key:wheelchair](https://wiki.openstreetmap.org/wiki/Key:wheelchair)

---

## 🤝 Contributing to OpenStreetMap

Help improve accessibility data for everyone:

1. Create account at [https://www.openstreetmap.org/user/new](https://www.openstreetmap.org/user/new)
2. Use the iD editor to add accessibility tags
3. Add wheelchair access, ramps, elevators to venues
4. Mark paths with width, surface type, incline
5. Your edits help the entire community!

---

**Ready to map the world! 🌍♿🗺️**
