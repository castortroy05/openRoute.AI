import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import UserPage from './pages/UserPage';
import PlacePage from './pages/PlacePage';
import ItineraryPage from './pages/ItineraryPage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';

const AppRouter = () => {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/user" element={<UserPage />} />
        <Route path="/place" element={<PlacePage />} />
        <Route path="/itinerary" element={<ItineraryPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </Router>
  );
};

export default AppRouter;
