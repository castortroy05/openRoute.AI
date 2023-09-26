import React, { useState } from 'react';
import { Form } from 'react-bootstrap';

const DarkModeToggle = () => {
  const [darkMode, setDarkMode] = useState(false);

  const handleDarkModeChange = (event) => {
    const isDarkMode = event.target.checked;
    setDarkMode(isDarkMode);
    document.body.classList.toggle('dark-mode', isDarkMode);
  };

  return (
    <Form>
      <Form.Check 
        type="switch"
        id="dark-mode-switch"
        label={darkMode ? 'Dark Mode' : 'Light Mode'}
        checked={darkMode}
        onChange={handleDarkModeChange}
      />
    </Form>
  );
};

export default DarkModeToggle;
