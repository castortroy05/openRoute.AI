import React from 'react';
import { Container, Row, Col, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import '../styles/App.scss';

const PlacePage = () => {
  return (
    <Container className="page-container">
      <Row className="justify-content-center align-items-center">
        <Col xs={12} md={6}>
          <h1>Place Page</h1>
          <p>Explore various places here. More features coming soon!</p>
          <Link to="/">
            <Button variant="secondary" className="mt-3">Go back to Home</Button>
          </Link>
        </Col>
      </Row>
    </Container>
  );
};

export default PlacePage;
