import React from 'react';
import { Navbar, Nav, Container } from 'react-bootstrap';
import { NavLink } from 'react-router-dom'; // Import NavLink from react-router-dom
import DarkModeToggle from './DarkModeToggle';

const NavigationBar = () => {
  return (
    <Navbar expand="lg">
      <Container>
        <Navbar.Brand as={NavLink} to="/">G.W.A.P.A.</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav variant="pills" className="me-auto">
            <Nav.Item>
              <Nav.Link as={NavLink} to="/user" activeclassname="active">User</Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link as={NavLink} to="/place" activeclassname="active">Place</Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link as={NavLink} to="/itinerary" activeclassname="active">Itinerary</Nav.Link>
            </Nav.Item>
          </Nav>
        </Navbar.Collapse>
        <DarkModeToggle />
      </Container>
    </Navbar>
  );
};

export default NavigationBar;
