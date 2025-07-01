import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';

// Componentes de Layout e Páginas
import Navbar from './components/Navbar';
import HomePage from './pages/Home'; // Supondo que a home page esteja em /pages
import NotFoundPage from './pages/NotFoundPage'; // Supondo que a página 404 esteja em /pages

import ComponentList from './components/ComponentList';
import ComponentCard from './components/ComponentCard';
import ComponentDetail from './components/ComponentDetail';

import './App.css';

function App() {
  return (
    <Router>
      <Navbar />

      <main className="main-content">
        <Routes>
          {/* Rota para a página inicial */}
          <Route path="/" element={<HomePage />} />

          {/* --- ROTAS DE LISTA CONFIGURADAS DIRETAMENTE --- */}

          {/* Rota para a lista de CPUs */}
          <Route
            path="/cpus"
            element={
              <ComponentList
                componentType="cpus"
                componentNamePlural="Processadores"
                searchPlaceholder="Buscar por modelo de CPU..."
                renderItem={(item) => <ComponentCard component={item} componentType="cpus" />}
              />
            }
          />

          {/* Rota para a lista de GPUs */}
          <Route
            path="/gpus"
            element={
              <ComponentList
                componentType="gpus"
                componentNamePlural="Placas de Vídeo"
                searchPlaceholder="Buscar por modelo de GPU..."
                renderItem={(item) => <ComponentCard component={item} componentType="gpus" />}
              />
            }
          />

          {/* Rota para a lista de Placas-Mãe */}
          <Route
            path="/motherboards"
            element={
              <ComponentList
                componentType="motherboards"
                componentNamePlural="Placas-Mãe"
                searchPlaceholder="Buscar por modelo de Placa-Mãe..."
                renderItem={(item) => <ComponentCard component={item} componentType="motherboards" />}
              />
            }
          />

          {/* Rota para a lista de Memórias RAM */}
          <Route
            path="/rams"
            element={
              <ComponentList
                componentType="rams"
                componentNamePlural="Memórias RAM"
                searchPlaceholder="Buscar por modelo de RAM..."
                renderItem={(item) => <ComponentCard component={item} componentType="rams" />}
              />
            }
          />

          {/* Rota para a lista de Armazenamento */}
          <Route
            path="/storages"
            element={
              <ComponentList
                componentType="storages"
                componentNamePlural="Unidades de Armazenamento"
                searchPlaceholder="Buscar por modelo de SSD/HDD..."
                renderItem={(item) => <ComponentCard component={item} componentType="storages" />}
              />
            }
          />

          {/* Rota para a lista de Fontes */}
          <Route
            path="/psus"
            element={
              <ComponentList
                componentType="psus"
                componentNamePlural="Fontes de Alimentação"
                searchPlaceholder="Buscar por modelo de Fonte..."
                renderItem={(item) => <ComponentCard component={item} componentType="psus" />}
              />
            }
          />

          {/* --- ROTA DE DETALHES GENÉRICA (permanece a mesma) --- */}
          <Route path="/component/:componentType/:id" element={<ComponentDetail />} />

          {/* --- ROTAS DE FALLBACK (permanecem as mesmas) --- */}
          <Route path="/not-found" element={<NotFoundPage />} />
          <Route path="*" element={<Navigate to="/not-found" replace />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;