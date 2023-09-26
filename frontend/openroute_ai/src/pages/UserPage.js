import React, { useState } from 'react';
import { Container, Row, Col, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import '../styles/App.scss';

const UserPage = () => {
  // This is just a placeholder, replace with actual login state management
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  return (
    <Container className="page-container">
      <Row className="justify-content-center align-items-center">
        <Col xs={12} md={6}>
          {isLoggedIn ? (
            <>
              <h1>Welcome, [Username]!</h1>
              <p>This is your user profile.</p>
              {/* Render other user profile related components or information here */}
            </>
          ) : (
            <>
              <h1>User Page</h1>
              <p>You are not logged in. Please log in or register to access your user profile and other features.</p>
              <Link to="/login">
                <Button variant="primary" className="mt-3 mr-2">Log In</Button>
              </Link>
              <Link to="/register">
                <Button variant="secondary" className="mt-3">Register</Button>
              </Link>
            </>
          )}
          <Link to="/">
            <Button variant="warning" className="mt-3">Go back to Home</Button>
          </Link>
        </Col>
      </Row>
    </Container>
  );
};

export default UserPage;
