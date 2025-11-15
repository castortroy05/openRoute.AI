import React, { useState } from 'react';
import axios from 'axios';
import { Card, Button, Form, Alert, Spinner, Badge } from 'react-bootstrap';
import './RouteDisplay.css';

/**
 * RouteDisplay Component
 * Displays route calculation interface and results
 *
 * Props:
 * - places: Array of selected places for routing
 * - onRouteCalculated: Callback with route data
 * - showAccessibilityOptions: Boolean to show accessibility preferences
 */
const RouteDisplay = ({
  places = [],
  onRouteCalculated = null,
  showAccessibilityOptions = true
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [routeData, setRouteData] = useState(null);

  // Route preferences
  const [wheelchairAccessible, setWheelchairAccessible] = useState(false);
  const [avoidHighways, setAvoidHighways] = useState(false);
  const [avoidTolls, setAvoidTolls] = useState(false);

  const calculateRoute = async () => {
    if (places.length < 2) {
      setError('Please select at least 2 places to calculate a route');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const placeIds = places.map(p => p.id).join(',');

      const response = await axios.get('/api/routing/calculate/', {
        params: {
          place_ids: placeIds,
          wheelchair_accessible: wheelchairAccessible,
          avoid_highways: avoidHighways,
          avoid_tolls: avoidTolls
        },
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      setRouteData(response.data);

      if (onRouteCalculated) {
        onRouteCalculated(response.data);
      }

    } catch (err) {
      console.error('Route calculation error:', err);
      setError(
        err.response?.data?.error ||
        'Failed to calculate route. Please check your API configuration and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const formatDistance = (meters) => {
    if (meters < 1000) {
      return `${Math.round(meters)} m`;
    }
    return `${(meters / 1000).toFixed(2)} km`;
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  return (
    <div className="route-display">
      <Card>
        <Card.Header>
          <h5 className="mb-0">
            🗺️ Route Calculation
          </h5>
        </Card.Header>
        <Card.Body>
          {/* Selected Places */}
          <div className="selected-places mb-3">
            <strong>Selected Places ({places.length}):</strong>
            {places.length === 0 ? (
              <p className="text-muted small mt-2">No places selected</p>
            ) : (
              <ol className="mt-2 mb-0">
                {places.map((place, index) => (
                  <li key={place.id} className="small">
                    {place.name}
                    {place.accessibility_features?.includes('Wheelchair Accessible') && (
                      <Badge bg="success" className="ms-2">♿</Badge>
                    )}
                  </li>
                ))}
              </ol>
            )}
          </div>

          {/* Route Preferences */}
          {showAccessibilityOptions && (
            <div className="route-preferences mb-3">
              <strong className="d-block mb-2">Route Preferences:</strong>

              <Form.Check
                type="checkbox"
                id="wheelchair-accessible"
                label="♿ Wheelchair Accessible Route"
                checked={wheelchairAccessible}
                onChange={(e) => setWheelchairAccessible(e.target.checked)}
                className="mb-2"
              />

              <Form.Check
                type="checkbox"
                id="avoid-highways"
                label="🚫 Avoid Highways"
                checked={avoidHighways}
                onChange={(e) => setAvoidHighways(e.target.checked)}
                className="mb-2"
              />

              <Form.Check
                type="checkbox"
                id="avoid-tolls"
                label="💰 Avoid Tolls"
                checked={avoidTolls}
                onChange={(e) => setAvoidTolls(e.target.checked)}
              />
            </div>
          )}

          {/* Calculate Button */}
          <Button
            variant="primary"
            onClick={calculateRoute}
            disabled={loading || places.length < 2}
            className="w-100 mb-3"
          >
            {loading ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                  className="me-2"
                />
                Calculating Route...
              </>
            ) : (
              '🚗 Calculate Route'
            )}
          </Button>

          {/* Error Message */}
          {error && (
            <Alert variant="danger" dismissible onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Route Results */}
          {routeData && routeData.route && (
            <div className="route-results">
              <Alert variant="success">
                <strong>✅ Route Calculated Successfully!</strong>
              </Alert>

              <div className="route-stats">
                <div className="stat-card">
                  <div className="stat-icon">📏</div>
                  <div className="stat-content">
                    <div className="stat-label">Distance</div>
                    <div className="stat-value">
                      {formatDistance(routeData.route.distance_meters)}
                    </div>
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-icon">⏱️</div>
                  <div className="stat-content">
                    <div className="stat-label">Duration</div>
                    <div className="stat-value">
                      {formatDuration(routeData.route.duration_seconds)}
                    </div>
                  </div>
                </div>

                {routeData.route.ascent_meters > 0 && (
                  <div className="stat-card">
                    <div className="stat-icon">⛰️</div>
                    <div className="stat-content">
                      <div className="stat-label">Elevation</div>
                      <div className="stat-value">
                        ↗ {Math.round(routeData.route.ascent_meters)}m
                        {' / '}
                        ↘ {Math.round(routeData.route.descent_meters)}m
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Turn-by-turn Instructions */}
              {routeData.route.instructions && routeData.route.instructions.length > 0 && (
                <div className="route-instructions mt-3">
                  <strong className="d-block mb-2">Turn-by-turn Directions:</strong>
                  <div className="instructions-list">
                    {routeData.route.instructions.slice(0, 10).map((instruction, index) => (
                      <div key={index} className="instruction-item">
                        <span className="instruction-number">{index + 1}</span>
                        <span className="instruction-text">{instruction.instruction || instruction.text}</span>
                        {instruction.distance && (
                          <span className="instruction-distance">
                            {formatDistance(instruction.distance)}
                          </span>
                        )}
                      </div>
                    ))}
                    {routeData.route.instructions.length > 10 && (
                      <div className="text-muted small text-center mt-2">
                        + {routeData.route.instructions.length - 10} more instructions
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Helpful Tips */}
          {!routeData && places.length >= 2 && (
            <div className="route-tips">
              <small className="text-muted">
                <strong>💡 Tip:</strong> Routes use OpenStreetMap data.
                {wheelchairAccessible && ' Wheelchair routes avoid steps and steep inclines.'}
              </small>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default RouteDisplay;
