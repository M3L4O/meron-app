import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './components/Home';
import CPUList from './components/CPUList'; // Wrapper
import CPUDetail from './components/CPUDetail'; // Detalhe específico
import GPUList from './components/GPUList'; // Wrapper
import GPUDetail from './components/GPUDetail'; // Detalhe específico
// Importe os detalhes e wrappers para outros tipos aqui
// import MotherboardList from './components/MotherboardList';
// import MotherboardDetail from './components/MotherboardDetail';

import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <Link to="/" className="nav-logo">Meron App</Link>
          <ul className="nav-links">
            <li><Link to="/">Home</Link></li>
            <li><Link to="/cpus">CPUs</Link></li>
            <li><Link to="/gpus">GPUs</Link></li>
            {/* Adicione mais links aqui */}
            {/* <li><Link to="/motherboards">Placas-Mãe</Link></li> */}
          </ul>
        </nav>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/cpus" element={<CPUList />} />
          <Route path="/cpus/:id" element={<CPUDetail />} />
          <Route path="/gpus" element={<GPUList />} />
          <Route path="/gpus/:id" element={<GPUDetail />} />
          {/* Adicione mais rotas aqui */}
          {/* <Route path="/motherboards" element={<MotherboardList />} /> */}
          {/* <Route path="/motherboards/:id" element={<MotherboardDetail />} /> */}
          <Route path="*" element={<h2>404 - Página Não Encontrada</h2>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;