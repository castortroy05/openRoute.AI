import React from 'react';
import { Container, Row, Col, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import '../styles/App.scss';

const HomePage = () => {
  // const [flags, setFlags] = useState([]);

 
  return (
    <Container className="homepage-container">
      <Row className="justify-content-center align-items-center">
        <Col xs={12} md={6}>
          
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
