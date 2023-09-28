import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, ListGroup } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faSuitcase, faList, faSignInAlt, faUserPlus, faHome, faUtensils, faWheelchair, faPaw, faBrain } from '@fortawesome/free-solid-svg-icons';
import AuthModal from '../components/AuthModal';
import '../styles/App.scss';

const UserPage = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showModal, setShowModal] = useState(false);

  return (
    <Container className="page-container">
      <Row className="justify-content-center align-items-center">
        <Col xs={12} md={6}>
          <Card className="mb-3 text-center shadow-lg rounded">
            <Card.Body>
              {isLoggedIn ? (
                <>
                  <Card.Title className="display-4 mb-4"><FontAwesomeIcon icon={faUser} /> Welcome, [Username]!</Card.Title>
                  <Card.Text>Manage your profile, preferences, and explore your travel plans:</Card.Text>
                  <ListGroup variant="flush" className="mb-3">
                    <ListGroup.Item><FontAwesomeIcon icon={faSuitcase} /> Trips: View and manage your upcoming and past trips.</ListGroup.Item>
                    <ListGroup.Item><FontAwesomeIcon icon={faList} /> Preferences: Update your dietary and accessibility preferences.</ListGroup.Item>
                    <ListGroup.Item><FontAwesomeIcon icon={faUtensils} /> Dietary Preferences: Specify your dietary needs like Vegan, Gluten-Free, etc.</ListGroup.Item>
                    <ListGroup.Item><FontAwesomeIcon icon={faWheelchair} /> Accessibility Requirements: Ensure your trips are comfortable and accessible.</ListGroup.Item>
                  </ListGroup>
                  <Card.Text>Optimize your travel experiences with personalized preferences and intelligent planning!</Card.Text>
                </>
              ) : (
                <>
                  <Card.Title className="display-4 mb-4">Unlock Personalized Travel Experiences!</Card.Title>
                  <Card.Text>Register now and gain access to a suite of personalized and intelligent travel planning features:</Card.Text>
                  <ListGroup variant="flush" className="mb-3">
                    <ListGroup.Item><FontAwesomeIcon icon={faSuitcase} /> Manage and optimize your trips.</ListGroup.Item>
                    <ListGroup.Item><FontAwesomeIcon icon={faList} /> Set your travel preferences for a tailored experience.</ListGroup.Item>
                    <ListGroup.Item><FontAwesomeIcon icon={faUtensils} /> Dietary Preferences: Specify your dietary needs like Vegan, Gluten-Free, etc.</ListGroup.Item>
                    <ListGroup.Item><FontAwesomeIcon icon={faWheelchair} /> Accessibility Requirements: Ensure your trips are comfortable and accessible.</ListGroup.Item>
                  </ListGroup>
                  <Card.Text>Don’t miss out on optimizing your travel experiences with us!</Card.Text>
                  <Button variant="primary" className="mt-3 mr-2" onClick={() => setShowModal(true)}><FontAwesomeIcon icon={faSignInAlt} /> Log In</Button>
                  <Button variant="secondary" className="mt-3" onClick={() => setShowModal(true)}><FontAwesomeIcon icon={faUserPlus} /> Register</Button>
                </>
              )}
              <Link to="/">
                <Button variant="warning" className="mt-3"><FontAwesomeIcon icon={faHome} /> Go back to Home</Button>
              </Link>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      <AuthModal show={showModal} onHide={() => setShowModal(false)} />
    </Container>
  );
};

export default UserPage;
