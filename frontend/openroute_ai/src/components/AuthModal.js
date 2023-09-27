// AuthModal.js
import React, { useState } from 'react';
import { Modal, Tabs, Tab, Button } from 'react-bootstrap';
import LoginForm from './LoginForm'; // Extract the form from LoginPage to a new component
import RegisterForm from './RegisterForm'; // Extract the form from RegisterPage to a new component
import '../styles/App.scss';

const AuthModal = ({ show, onHide }) => {
  const [activeTab, setActiveTab] = useState('login');

  return (
    <Modal show={show} onHide={onHide} centered className='modal'>
      <Modal.Header closeButton>
        <Modal.Title>{activeTab === 'login' ? 'Login' : 'Register'}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k)}>
          <Tab eventKey="login" title="Login">
            <LoginForm />
          </Tab>
          <Tab eventKey="register" title="Register">
            <RegisterForm />
          </Tab>
        </Tabs>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default AuthModal;
