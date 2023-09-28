import React from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCompass, faBrain, faCalendarAlt, faSyncAlt, faAdjust } from '@fortawesome/free-solid-svg-icons';
import '../styles/App.scss';

const HomePage = () => {
  return (
    <Container className="homepage-container">
      <Row className="justify-content-center align-items-center">
        <Col xs={12} md={6}>
          <Card className="mb-3 ">
            <Card.Body>
              <Card.Title className="display-4 mb-4 text-center">Welcome to <span className="text-primary">GWAPA</span>!</Card.Title>
              
             
                <Card.Body>
                  <Card.Title className='text-center'><FontAwesomeIcon icon={faCompass} className="mr-2 text-primary" /> G - Guide Wisely</Card.Title>
                  <Card.Text>Experience intelligent, AI-driven guidance designed to navigate you through your journeys. Whether you're exploring new destinations or revisiting familiar ones, our guidance ensures you're informed, prepared, and can make decisions with confidence, enhancing your overall travel experience.</Card.Text>
                </Card.Body>
              
                <Card.Body>
                  <Card.Title className='text-center'><FontAwesomeIcon icon={faBrain} className="mr-2 text-warning" /> W - Work Smartly</Card.Title>
                  <Card.Text>Optimize your schedules and routes with the power of AI. Our smart solutions analyze various factors like traffic, weather, and personal preferences to suggest the most efficient routes and schedules, saving you time and effort, allowing you to focus on enjoying your journey.</Card.Text>
                </Card.Body>
              
              
             
                <Card.Body>
                  <Card.Title className='text-center'><FontAwesomeIcon icon={faAdjust} className="mr-2 text-success" /> A - Act Proactively</Card.Title>
                  <Card.Text>Empower your travels with proactive actions and decisions. By combining AI-driven guidance and intelligent analysis, we enable you to anticipate potential issues, adapt your plans swiftly, and make the most out of every moment, ensuring a smoother and more enjoyable travel experience.</Card.Text>
                </Card.Body>
              
              
              
                <Card.Body>
                  <Card.Title className='text-center'><FontAwesomeIcon icon={faCalendarAlt} className="mr-2 text-info" /> P - Plan Effectively</Card.Title>
                  <Card.Text>Transform your travel planning with personalized, intelligent itineraries. Our AI analyzes your preferences, constraints, and goals to craft optimal itineraries, manage your plans seamlessly, and offer real-time adjustments, making travel planning a breeze and your journeys more fulfilling.</Card.Text>
                </Card.Body>
              
              
              
                <Card.Body>
                  <Card.Title className='text-center'><FontAwesomeIcon icon={faSyncAlt} className="mr-2 text-danger" /> A - Adapt Accordingly</Card.Title>
                  <Card.Text>Enhance your adaptability with real-time updates and intelligent recommendations. Our AI continuously monitors various factors and user preferences to provide instant alerts and suggestions, allowing you to adapt your plans accordingly, overcome unexpected challenges, and enjoy your travels to the fullest.</Card.Text>
                </Card.Body>
              
              
              <Card.Body className="text-muted mb-3">
                GWAPA is your AI-powered virtual assistant for optimizing travel itineraries and schedules. Whether you are planning a leisure trip or managing daily tasks, GWAPA provides real-time, user-friendly, and intelligent solutions to guide you wisely, work smartly, plan effectively, and adapt accordingly. Explore, plan, and travel with ease and efficiency with GWAPA!
              </Card.Body>
              
              <Link to="/user">
                <Button variant="primary" className="mt-3">Start Your Intelligent Journey</Button>
              </Link>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default HomePage;
