import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { RiCpuLine } from 'react-icons/ri'; // Ícone para o título da página de detalhes
import './CPUDetail.css';

// Função auxiliar para "mocar" (simular) preço e disponibilidade
// Esta função é idêntica à de CPUList, para manter a consistência
const mockPriceAndAvailabilityDetail = () => {
  const availabilityOptions = ['Disponível', 'Indisponível'];
  return {
    price: (Math.random() * (4500 - 500) + 500).toFixed(2),
    availability: availabilityOptions[Math.floor(Math.random() * availabilityOptions.length)]
  };
};

function CPUDetail() {
  const { id } = useParams();
  const navigate = useNavigate(); // Hook para navegação
  const [cpu, setCpu] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mockedData, setMockedData] = useState({}); // Novo estado para dados mockados

  useEffect(() => {
    const fetchCpuDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/api/cpus/${id}/`);
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('CPU não encontrada.');
          }
          throw new Error(`Erro HTTP! Status: ${response.status}`);
        }
        const data = await response.json();
        setCpu(data);
        setMockedData(mockPriceAndAvailabilityDetail()); // Moca os dados aqui
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    };

    fetchCpuDetail();
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
          {/* Use button onClick para navegar para trás */}
          <button onClick={handleBackButtonClick} className="back-button">Voltar para a lista de CPUs</button>
        </div>
      </div>
    );
  }

  if (!cpu) {
    return (
      <div className="detail-page-container">
        <p>Nenhum dado de CPU disponível.</p>
        <button onClick={handleBackButtonClick} className="back-button">Voltar para a lista de CPUs</button>
      </div>
    );
  }

  // Renderiza os detalhes da CPU
  return (
    <div className="detail-page-container"> {/* Container principal da página de detalhes */}
      <header className="detail-header-section"> {/* Seção de cabeçalho */}
        <div className="detail-title-group">
          <RiCpuLine className="detail-icon" /> {/* Ícone maior no título da página */}
          <h1>{cpu.manufacturer} {cpu.model}</h1>
        </div>
        <div className="detail-summary-info"> {/* Resumo de preço e disponibilidade */}
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
          <div className="spec-item"><span className="spec-label">Fabricante:</span> <span className="spec-value">{cpu.manufacturer}</span></div>
          <div className="spec-item"><span className="spec-label">Modelo:</span> <span className="spec-value">{cpu.model}</span></div>
          <div className="spec-item"><span className="spec-label">Soquete:</span> <span className="spec-value">{cpu.socket}</span></div>
          <div className="spec-item"><span className="spec-label">Consumo (TDP):</span> <span className="spec-value">{cpu.consumption} W</span></div>
        </div>

        <div className="detail-specs-section">
          <h2>Performance</h2>
          <div className="spec-item"><span className="spec-label">Número de Cores:</span> <span className="spec-value">{cpu.n_cores}</span></div>
          <div className="spec-item"><span className="spec-label">Clock Base:</span> <span className="spec-value">{cpu.base_clock_speed} GHz</span></div>
          <div className="spec-item"><span className="spec-label">Clock Boost:</span> <span className="spec-value">{cpu.boost_clock_speed} GHz</span></div>
          {cpu.integrated_gpu && <div className="spec-item"><span className="spec-label">Gráficos Integrados:</span> <span className="spec-value">{cpu.integrated_gpu}</span></div>}
          {cpu.l3_cache && <div className="spec-item"><span className="spec-label">Cache L3:</span> <span className="spec-value">{cpu.l3_cache}</span></div>}
          {cpu.process && <div className="spec-item"><span className="spec-label">Processo:</span> <span className="spec-value">{cpu.process}</span></div>}
        </div>

        {/* Você pode adicionar mais seções conforme necessário */}

        <button onClick={handleBackButtonClick} className="back-button detail-back-button">Voltar para a lista de CPUs</button>
      </main>
    </div>
  );
}

export default CPUDetail;