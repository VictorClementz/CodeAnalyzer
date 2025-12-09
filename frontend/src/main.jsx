import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import CodeAnalyzer from './Components/CodeAnalyzer';
import Login from './Components/Login';
import Signup from './Components/Signup';
import Dashboard from './Pages/Dashboard.jsx'
import ProjectDetail from './Pages/ProjectDetail';
import FileHistory from './Pages/FileHistory';
import Navbar from './Components/Navbar';
import ProtectedRoute from './Components/ProtectedRoute';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<CodeAnalyzer />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/projects/:projectId" 
          element={
            <ProtectedRoute>
              <ProjectDetail />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/projects/:projectId/files/:fileId" 
          element={
            <ProtectedRoute>
              <FileHistory />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);