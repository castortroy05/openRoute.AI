// UserPage.js
import React, { useState } from 'react';
import { Container, Row, Col, Button } from 'react-bootstrap';
import AuthModal from '../components/AuthModal';// Import the AuthModal component

const UserPage = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showModal, setShowModal] = useState(false);

  return (
    <Container className="page-container">
      <Row className="justify-content-center align-items-center">
        <Col xs={12} md={6}>
          {isLoggedIn ? (
            <>
              <h1>Welcome, [Username]!</h1>
              <p>This is your user profile.</p>
            </>
          ) : (
            <>
              <h1>User Page</h1>
              <p>You are not logged in. Please log in or register to access your user profile and other features.</p>
              <Button variant="primary" className="mt-3 mr-2" onClick={() => setShowModal(true)}>Log In</Button>
              <Button variant="secondary" className="mt-3" onClick={() => setShowModal(true)}>Register</Button>
            </>
          )}
          <Button variant="warning" className="mt-3">Go back to Home</Button>
        </Col>
      </Row>
      <AuthModal show={showModal} onHide={() => setShowModal(false)} />
    </Container>
  );
};

export default UserPage;
