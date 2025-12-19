import { useState } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import HomePage from '@/pages/HomePage';
import EvaluationPage from '@/pages/EvaluationPage';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/evaluation" element={<EvaluationPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
