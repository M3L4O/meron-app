import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MdMonitor } from 'react-icons/md'; // Ícone para o título da página de detalhes
import './GPUDetail.css';

// Função auxiliar para "mocar" (simular) preço e disponibilidade
const mockPriceAndAvailabilityDetail = () => {
  const availabilityOptions = ['Disponível', 'Indisponível'];
  return {
    price: (Math.random() * (7000 - 1000) + 1000).toFixed(2), // Preços de GPU
    availability: availabilityOptions[Math.floor(Math.random() * availabilityOptions.length)]
  };
};

function GPUDetail() {
  const { id } = useParams();
  const navigate = useNavigate(); // Hook para navegação
  const [gpu, setGpu] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mockedData, setMockedData] = useState({}); // Novo estado para dados mockados

  useEffect(() => {
    const fetchGpuDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/api/gpus/${id}/`);
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('GPU não encontrada.');
          }
          throw new Error(`Erro HTTP! Status: ${response.status}`);
        }
        const data = await response.json();
        setGpu(data);
        setMockedData(mockPriceAndAvailabilityDetail()); // Moca os dados aqui
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    };

    fetchGpuDetail();
  }, [id]);

  // Função para lidar com o botão de voltar
  const handleBackButtonClick = () => {
    // navigate(-1) simula o botão "voltar" do navegador
    // Mas ele não leva o estado. Para levar o estado, precisaríamos
    // armazená-lo na página de lista antes de navegar para cá.
    // Como a lista já salva o estado, navegar para trás é o suficiente.
    navigate(-1); 
  };

  if (loading) {
    return (
      <div className="detail-page-container">
        <div className="detail-loading-skeleton">
          <div className="skeleton-title-line"></div>
          <div className="skeleton-price-line"></div>
          <div className="skeleton-section-title"></div>
          <div className="skeleton-specs-block">
            <div className="skeleton-spec-line"></div>
            <div className="skeleton-spec-line"></div>
            <div className="skeleton-spec-line"></div>
          </div>
          <div className="skeleton-section-title"></div>
          <div className="skeleton-specs-block">
            <div className="skeleton-spec-line"></div>
            <div className="skeleton-spec-line"></div>
          </div>
          <div className="skeleton-back-button"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="detail-page-container">
        <div className="error-message detail-error-message">
          <p>Erro: {error.message}</p>
          <button onClick={handleBackButtonClick} className="back-button">Voltar para a lista de GPUs</button>
        </div>
      </div>
    );
  }

  if (!gpu) {
    return (
      <div className="detail-page-container">
        <p>Nenhum dado de GPU disponível.</p>
        <button onClick={handleBackButtonClick} className="back-button">Voltar para a lista de GPUs</button>
      </div>
    );
  }

  // Renderiza os detalhes da GPU
  return (
    <div className="detail-page-container">
      <header className="detail-header-section">
        <div className="detail-title-group">
          <MdMonitor className="detail-icon" /> {/* Ícone da GPU */}
          <h1>{gpu.manufacturer} {gpu.model}</h1>
        </div>
        <div className="detail-summary-info">
          {mockedData.price && (
            <p className="detail-price">
              <strong>Preço:</strong> R$ {parseFloat(mockedData.price).toFixed(2).replace('.', ',')}
            </p>
          )}
          {mockedData.availability && (
            <p className="detail-availability">
              <strong>Disponibilidade:</strong> {mockedData.availability}
            </p>
          )}
        </div>
      </header>

      <main className="detail-main-content">
        <div className="detail-specs-section">
          <h2>Informações Gerais</h2>
          <div className="spec-item"><span className="spec-label">Fabricante:</span> <span className="spec-value">{gpu.manufacturer}</span></div>
          <div className="spec-item"><span className="spec-label">Modelo:</span> <span className="spec-value">{gpu.model}</span></div>
          <div className="spec-item"><span className="spec-label">Consumo (TDP):</span> <span className="spec-value">{gpu.consumption} W</span></div>
        </div>

        <div className="detail-specs-section">
          <h2>Memória e Clock</h2>
          <div className="spec-item"><span className="spec-label">VRAM:</span> <span className="spec-value">{gpu.vram} GB</span></div>
          <div className="spec-item"><span className="spec-label">VRAM speed:</span> <span className="spec-value">{gpu.vram_speed} MHz</span></div>
        </div>

        <button onClick={handleBackButtonClick} className="back-button detail-back-button">Voltar para a lista de GPUs</button>
      </main>
    </div>
  );
}

export default GPUDetail;