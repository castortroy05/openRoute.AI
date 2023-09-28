import React, { useState } from 'react';
import { Container, Row, Col, Button, ListGroup } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMapPin, faSearch, faInfoCircle, faSignInAlt, faUserPlus, faHome } from '@fortawesome/free-solid-svg-icons';
import AuthModal from '../components/AuthModal'; // Import the AuthModal component
import '../styles/App.scss';

const PlacePage = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showModal, setShowModal] = useState(false);

  return (
    <Container className="page-container">
      <Row className="justify-content-center align-items-center">
        <Col xs={12} md={6}>
          {isLoggedIn ? (
            <>
              <h1><FontAwesomeIcon icon={faMapPin} /> Discover and Explore with Intelligent Place Finder!</h1>
              <p>Welcome to the Place Page, your gateway to exploring new destinations and experiences. Here’s what you can do:</p>
              <ListGroup variant="flush">
                <ListGroup.Item><FontAwesomeIcon icon={faSearch} /> Search Places: Find new destinations and experiences with ease.</ListGroup.Item>
                <ListGroup.Item><FontAwesomeIcon icon={faInfoCircle} /> Detailed Information: Get comprehensive details about each place.</ListGroup.Item>
                <ListGroup.Item><FontAwesomeIcon icon={faMapPin} /> Add to Itinerary: Seamlessly add places to your travel plan.</ListGroup.Item>
              </ListGroup>
              <p>Start exploring and add new destinations to your itinerary with Intelligent Place Finder!</p>
            </>
          ) : (
            <>
              <h1>Unlock the World with Intelligent Place Finder!</h1>
              <p>Register now and gain access to a suite of intelligent place finding features:</p>
              <ListGroup variant="flush">
                <ListGroup.Item><FontAwesomeIcon icon={faSearch} /> Explore new destinations with ease.</ListGroup.Item>
                <ListGroup.Item><FontAwesomeIcon icon={faInfoCircle} /> Access detailed information about each place.</ListGroup.Item>
                <ListGroup.Item><FontAwesomeIcon icon={faMapPin} /> Add to Itinerary: Seamlessly add places to your travel plan.</ListGroup.Item>
              </ListGroup>
              <p>Don’t miss out on discovering the world with us!</p>
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

export default PlacePage;
