// RegisterForm.js
import React, { useState } from 'react';
import { Form, Button, Alert } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faEnvelope, faLock } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import '../styles/App.scss';

const RegisterForm = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState([]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const validateForm = () => {
    const newErrors = [];
    // Validation logic here
    setErrors(newErrors);
    return newErrors.length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    try {
      const response = await axios.post('http://localhost:8000/register/', formData);
      console.log(response.data); // User registered successfully
    } catch (error) {
      console.error('There was an error registering!', error);
    }
  };
  

  return (
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
  );
};

export default RegisterForm;
