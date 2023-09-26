import React from 'react';
import { Container, Row, Col, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import '../styles/App.scss';

const UserPage = () => {
  return (
    <Container className="page-container">
      <Row className="justify-content-center align-items-center">
        <Col xs={12} md={6}>
          <h1>User Page</h1>
          <p>This is the User Page. More features coming soon!</p>
          <Link to="/">
            <Button variant="secondary" className="mt-3">Go back to Home</Button>
          </Link>
        </Col>
      </Row>
    </Container>
  );
};

export default UserPage;
