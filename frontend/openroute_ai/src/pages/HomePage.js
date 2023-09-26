import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Button, Carousel } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import '../styles/App.scss';

const HomePage = () => {
  const [flags, setFlags] = useState([]);

  useEffect(() => {
    // Fetch flags from the backend
    fetch('http://localhost:8000/media/')
      .then((response) => response.json())
      .then((data) => setFlags(data.flags));
  }, []);

  return (
    <Container className="homepage-container">
      <Row className="justify-content-center align-items-center">
        <Col xs={12} md={6}>
          <Carousel>
            {flags.map((flag, index) => (
              <Carousel.Item key={index}>
                <img
                  className="d-block w-100 flag-image"
                  src={`/${flag}`}
                  alt="Country Flag"
                />
              </Carousel.Item>
            ))}
          </Carousel>
          <h1>Welcome to OpenRoute.AI!</h1>
          <p>Explore and plan your journeys with ease.</p>
          <Link to="/user">
            <Button variant="secondary" className="mt-3">Get Started</Button>
          </Link>
        </Col>
      </Row>
    </Container>
  );
};

export default HomePage;
