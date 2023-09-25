import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
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
      <Switch>
        <Route path="/" exact component={HomePage} />
        <Route path="/user" component={UserPage} />
        <Route path="/place" component={PlacePage} />
        <Route path="/itinerary" component={ItineraryPage} />
        <Route path="/register" component={RegisterPage} />
        <Route path="/login" component={LoginPage} />
      </Switch>
    </Router>
  );
};

export default AppRouter;
