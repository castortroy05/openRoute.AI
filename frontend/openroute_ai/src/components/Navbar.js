import React from 'react';
import { Navbar, Nav, Container, Badge } from 'react-bootstrap';
import { NavLink } from 'react-router-dom'; // Import NavLink from react-router-dom
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faMapMarkerAlt, faSuitcaseRolling, faHome } from '@fortawesome/free-solid-svg-icons';
import DarkModeToggle from './DarkModeToggle';
import '../styles/App.scss';

const NavigationBar = () => {
  return (
    <Navbar expand="lg" className="navbar-custom">
      <Container>
      <Navbar.Brand as={NavLink} to="/" className={window.location.pathname === "/" ? "home-brand" : ""}>
  <FontAwesomeIcon icon={faHome} /> G.W.A.P.A. <Badge variant="secondary">AI</Badge>
</Navbar.Brand>

        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav variant="pills" className="me-auto">
            <Nav.Item>
              <Nav.Link as={NavLink} to="/user" activeClassName="active">
                <FontAwesomeIcon icon={faUser} /> User
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link as={NavLink} to="/place" activeClassName="active">
                <FontAwesomeIcon icon={faMapMarkerAlt} /> Place
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link as={NavLink} to="/itinerary" activeClassName="active">
                <FontAwesomeIcon icon={faSuitcaseRolling} /> Itinerary
              </Nav.Link>
            </Nav.Item>
          </Nav>
        </Navbar.Collapse>
        <DarkModeToggle />
      </Container>
    </Navbar>
  );
};

export default NavigationBar;
