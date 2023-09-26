import React, { useState } from 'react';
import { Form, Button, Container, Row, Col, Alert } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faEnvelope, faLock } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import '../styles/App.scss';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState([]);
  const history = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const validateForm = () => {
    const newErrors = [];
    // Add form validation logic here
    // Push error messages to newErrors array
    setErrors(newErrors);
    return newErrors.length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    // Call API to register user
    // On success, redirect to login page
    history.push('/login');
  };

  return (
    <Container className="register-container">
      <Row className="justify-content-md-center">
        <Col md="6">
          <h2>Register</h2>
          {errors.map((error, index) => (
            <Alert key={index} variant="danger">
              {error}
            </Alert>
          ))}
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="username">
              <Form.Label><FontAwesomeIcon icon={faUser} /> Username</Form.Label>
              <Form.Control type="text" name="username" value={formData.username} onChange={handleChange} required />
            </Form.Group>
            <Form.Group controlId="email">
              <Form.Label><FontAwesomeIcon icon={faEnvelope} /> Email</Form.Label>
              <Form.Control type="email" name="email" value={formData.email} onChange={handleChange} required />
            </Form.Group>
            <Form.Group controlId="password">
              <Form.Label><FontAwesomeIcon icon={faLock} /> Password</Form.Label>
              <Form.Control type="password" name="password" value={formData.password} onChange={handleChange} required />
            </Form.Group>
            <Button variant="primary" type="submit" className="register-button">
              Register
            </Button>
          </Form>
        </Col>
      </Row>
    </Container>
  );
};

export default RegisterPage;
