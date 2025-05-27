import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './components/Home';
import ComponentList from './components/ComponentList';
import ComponentCard from './components/ComponentCard'; // Importamos o card para usar na renderItem
// Importa os componentes de detalhe...
import CPUDetail from './components/CPUDetail';
import GPUDetail from './components/GPUDetail';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <main>
          <Routes>
            <Route path="/" element={<Home />} />

            <Route
              path="/cpus"
              element={
                <ComponentList
                  componentType="cpus"
                  componentNameSingular="Processador"
                  componentNamePlural="Processadores"
                  searchPlaceholder="Buscar por modelo de CPU..."

                  renderItem={(item) => <ComponentCard item={item} type="cpus" />}
                />
              }
            />

            <Route
              path="/gpus"
              element={
                <ComponentList
                  componentType="gpus"
                  componentNameSingular="Placa de Vídeo"
                  componentNamePlural="Placas de Vídeo"
                  searchPlaceholder="Buscar por modelo de GPU..."
                  renderItem={(item) => <ComponentCard item={item} type="gpus" />}
                />
              }
            />
            <Route path="/cpus/:id" element={<CPUDetail />} />
            <Route path="/gpus/:id" element={<GPUDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;