import React, { useState } from 'react';
import { Container, Row, Col, Button, ListGroup } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMapMarkedAlt, faClock, faSun, faUserCog, faSignInAlt, faUserPlus, faHome } from '@fortawesome/free-solid-svg-icons';
import AuthModal from '../components/AuthModal'; // Import the AuthModal component
import '../styles/App.scss';

const ItineraryPage = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showModal, setShowModal] = useState(false);

  return (
    <Container className="page-container">
      <Row className="justify-content-center align-items-center">
        <Col xs={12} md={6}>
          {isLoggedIn ? (
            <>
              <h1><FontAwesomeIcon icon={faMapMarkedAlt} /> Embark on Your Journey with Intelligent Itinerary Planning!</h1>
              <p>Welcome to the Itinerary Page, your one-stop solution for crafting the perfect travel plan. Here’s what you can do:</p>
              <ListGroup variant="flush">
                <ListGroup.Item><FontAwesomeIcon icon={faClock} /> Optimize Routes: Find the most efficient paths with our AI-driven algorithms.</ListGroup.Item>
                <ListGroup.Item><FontAwesomeIcon icon={faUserCog} /> Personalize Plans: Tailor your itinerary to your preferences.</ListGroup.Item>
                <ListGroup.Item><FontAwesomeIcon icon={faSun} /> Real-time Adaptation: Receive instant updates based on real-time conditions.</ListGroup.Item>
                <ListGroup.Item><FontAwesomeIcon icon={faMapMarkedAlt} /> Explore Destinations: Discover new places and experiences.</ListGroup.Item>
              </ListGroup>
              <p>Start planning your journey and make the most out of every moment with Intelligent Itinerary Planning!</p>
            </>
          ) : (
            <>
              <h1>Unlock Your Ultimate Travel Companion!</h1>
              <p>Register now and gain access to a suite of intelligent travel planning features:</p>
              <ListGroup variant="flush">
                <ListGroup.Item><FontAwesomeIcon icon={faClock} /> Optimize Routes: Find the most efficient paths with our AI-driven algorithms.</ListGroup.Item>
                <ListGroup.Item><FontAwesomeIcon icon={faUserCog} /> Personalize Plans: Tailor your itinerary to your preferences.</ListGroup.Item>
                <ListGroup.Item><FontAwesomeIcon icon={faSun} /> Real-time Adaptation: Receive instant updates based on real-time conditions.</ListGroup.Item>
                <ListGroup.Item><FontAwesomeIcon icon={faMapMarkedAlt} /> Explore Destinations: Discover new places and experiences.</ListGroup.Item>
              </ListGroup>
              <p>Don’t miss out on crafting your perfect journey with us!</p>
              <Button variant="primary" className="mt-3 mr-2" onClick={() => setShowModal(true)}><FontAwesomeIcon icon={faSignInAlt} /> Log In</Button>
              <Button variant="secondary" className="mt-3" onClick={() => setShowModal(true)}><FontAwesomeIcon icon={faUserPlus} /> Register</Button>
            </>
          )}
          <Link to="/">
            <Button variant="warning" className="mt-3"><FontAwesomeIcon icon={faHome} /> Go back to Home</Button>
          </Link>
        </Col>
      </Row>
      <AuthModal show={showModal} onHide={() => setShowModal(false)} />
    </Container>
  );
};

export default ItineraryPage;
