import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import ProfileForm from './pages/ProfileForm';
import PublicInvitation from './pages/PublicInvitation';
import RSVPManagement from './pages/RSVPManagement';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            <Route path="/admin/profile/new" element={<ProfileForm />} />
            <Route path="/admin/profile/:profileId/edit" element={<ProfileForm />} />
            <Route path="/admin/profile/:profileId/rsvps" element={<RSVPManagement />} />
            <Route path="/invite/:slug" element={<PublicInvitation />} />
          </Routes>
        </BrowserRouter>
      </div>
    </AuthProvider>
  );
}

export default App;
