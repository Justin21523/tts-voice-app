// ============ src/App.jsx ============
import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import TTSPage from './pages/TTSPage';
import VCPage from './pages/VCPage';

// Import styles
import './styles/variables.css';
import './styles/global.css';
import './styles/components.css';
import './styles/pages.css';

const App = () => {
  return (
    <Router>
      <div className="app">
        <nav className="nav">
          <div className="nav-container">
            <NavLink to="/" className="nav-brand">
              🎙️ Voice App
            </NavLink>
            <ul className="nav-links">
              <li>
                <NavLink
                  to="/"
                  className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                  end
                >
                  Text-to-Speech
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/vc"
                  className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                >
                  Voice Conversion
                </NavLink>
              </li>
            </ul>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<TTSPage />} />
            <Route path="/vc" element={<VCPage />} />
          </Routes>
        </main>

        <footer className="footer" style={{
          marginTop: 'var(--spacing-xl)',
          padding: 'var(--spacing-lg) 0',
          borderTop: '1px solid var(--border-color)',
          textAlign: 'center',
          color: 'var(--text-muted)'
        }}>
          <div className="container">
            <p>Voice App MVP - Personal Voice Synthesis & Conversion Tool</p>
          </div>
        </footer>
      </div>
    </Router>
  );
};

export default App;