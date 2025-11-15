import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './MapView.css';

// Fix Leaflet default marker icons
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

// Custom icons for different place types
const createCustomIcon = (color) => {
  return L.icon({
    iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
  });
};

const placeTypeIcons = {
  R: createCustomIcon('red'),      // Restaurant
  H: createCustomIcon('blue'),     // Hotel
  A: createCustomIcon('green'),    // Attraction
  M: createCustomIcon('violet'),   // Museum
  P: createCustomIcon('orange'),   // Park
  default: DefaultIcon
};

// Component to update map view when center/zoom changes
function ChangeView({ center, zoom }) {
  const map = useMap();

  useEffect(() => {
    if (center) {
      map.setView(center, zoom);
    }
  }, [center, zoom, map]);

  return null;
}

/**
 * MapView Component
 * Displays an interactive map using OpenStreetMap tiles via Leaflet
 *
 * Props:
 * - places: Array of place objects with {id, name, latitude, longitude, place_type, accessibility_features}
 * - route: Route geometry from OpenRouteService (GeoJSON LineString)
 * - center: Map center [lat, lng]
 * - zoom: Initial zoom level
 * - showAccessibilityFeatures: Boolean to show accessibility markers
 * - onPlaceClick: Callback when a place marker is clicked
 */
const MapView = ({
  places = [],
  route = null,
  center = [51.505, -0.09],
  zoom = 13,
  showAccessibilityFeatures = false,
  onPlaceClick = null,
  height = '500px'
}) => {
  const [mapCenter, setMapCenter] = useState(center);
  const [mapZoom, setMapZoom] = useState(zoom);

  useEffect(() => {
    // Auto-center on places if provided
    if (places && places.length > 0) {
      const avgLat = places.reduce((sum, p) => sum + parseFloat(p.latitude), 0) / places.length;
      const avgLng = places.reduce((sum, p) => sum + parseFloat(p.longitude), 0) / places.length;
      setMapCenter([avgLat, avgLng]);
    } else {
      setMapCenter(center);
    }
  }, [places, center]);

  // Convert route geometry to Leaflet Polyline format
  const getRouteCoordinates = () => {
    if (!route || !route.geometry || !route.geometry.coordinates) {
      return [];
    }

    // GeoJSON uses [longitude, latitude], Leaflet uses [latitude, longitude]
    return route.geometry.coordinates.map(coord => [coord[1], coord[0]]);
  };

  const routeCoordinates = getRouteCoordinates();

  return (
    <div className="map-view-container" style={{ height }}>
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        {/* OpenStreetMap tile layer - FREE and open source */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        {/* Alternative tile layers (commented out, can be enabled) */}
        {/*
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          maxZoom={19}
        />
        */}

        {/* Update view when center/zoom changes */}
        <ChangeView center={mapCenter} zoom={mapZoom} />

        {/* Place markers */}
        {places && places.map((place) => {
          const icon = placeTypeIcons[place.place_type] || placeTypeIcons.default;
          const hasAccessibility = place.accessibility_features &&
                                   place.accessibility_features.includes('Wheelchair Accessible');

          return (
            <Marker
              key={place.id}
              position={[parseFloat(place.latitude), parseFloat(place.longitude)]}
              icon={icon}
              eventHandlers={{
                click: () => {
                  if (onPlaceClick) {
                    onPlaceClick(place);
                  }
                },
              }}
            >
              <Popup>
                <div className="map-popup">
                  <h6>{place.name}</h6>
                  <p className="text-muted small">{place.address || 'Address not available'}</p>

                  {hasAccessibility && (
                    <div className="accessibility-badge">
                      <span className="badge bg-success">
                        ♿ Wheelchair Accessible
                      </span>
                    </div>
                  )}

                  {place.accessibility_features && (
                    <div className="accessibility-info">
                      <small><strong>Accessibility:</strong></small>
                      <small className="d-block">{place.accessibility_features}</small>
                    </div>
                  )}

                  {place.place_type && (
                    <small className="text-muted">
                      Type: {getPlaceTypeName(place.place_type)}
                    </small>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Route polyline */}
        {routeCoordinates.length > 0 && (
          <Polyline
            positions={routeCoordinates}
            color="#3388ff"
            weight={5}
            opacity={0.7}
            smoothFactor={1}
          />
        )}
      </MapContainer>

      {/* Map legend */}
      {places && places.length > 0 && (
        <div className="map-legend">
          <small><strong>Legend:</strong></small>
          <div className="legend-items">
            <div className="legend-item">
              <span className="legend-marker" style={{ backgroundColor: '#d32f2f' }}></span>
              <span>Restaurant</span>
            </div>
            <div className="legend-item">
              <span className="legend-marker" style={{ backgroundColor: '#1976d2' }}></span>
              <span>Hotel</span>
            </div>
            <div className="legend-item">
              <span className="legend-marker" style={{ backgroundColor: '#388e3c' }}></span>
              <span>Attraction</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper function to get place type name
function getPlaceTypeName(code) {
  const types = {
    'R': 'Restaurant',
    'H': 'Hotel',
    'A': 'Attraction',
    'S': 'Shopping',
    'T': 'Theatre',
    'CI': 'Cinema',
    'Ba': 'Bar',
    'CL': 'Club',
    'G': 'Gallery',
    'L': 'Library',
    'Z': 'Zoo',
    'AQ': 'Aquarium',
    'Be': 'Beach',
    'TP': 'Theme Park',
    'M': 'Museum',
    'P': 'Park',
    'O': 'Other'
  };
  return types[code] || 'Unknown';
}

export default MapView;
