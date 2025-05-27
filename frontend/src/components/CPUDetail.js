import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { IoIosArrowBack } from 'react-icons/io';
import ComponentIcon from './ComponentIcon'; // Reutilizamos o nosso componente de ícone
import './CPUDetail.css'; // Um novo CSS para a página de detalhes

const CPUDetail = () => {
    // useParams para pegar o 'id' da URL (ex: /cpus/algum-uuid)
    const { id } = useParams();
    const [cpu, setCpu] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCpuDetails = async () => {
            setLoading(true);
            try {
                // Busca os dados do endpoint específico para esta CPU
                const response = await fetch(`http://localhost:8000/api/cpus/${id}/`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                setCpu(data);
            } catch (err) {
                setError(err);
                console.error("Erro ao buscar detalhes da CPU:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchCpuDetails();
    }, [id]); // O useEffect executa sempre que o 'id' na URL mudar

    if (loading) {
        // Poderíamos criar um "esqueleto" de loading mais elaborado para a página de detalhes
        return <div className="detail-container loading">A carregar detalhes...</div>;
    }

    if (error) {
        return (
            <div className="detail-container error">
                <h2>Erro ao Carregar</h2>
                <p>{error.message}</p>
                <Link to="/cpus" className="back-button">
                    <IoIosArrowBack /> Voltar para a lista
                </Link>
            </div>
        );
    }

    if (!cpu) {
        return <div>Processador não encontrado.</div>;
    }

    // Separa os dados voláteis para facilitar o acesso
    const offers = cpu.volatile_data || [];

    return (
        <div className="detail-container">
            <header className="detail-header">
                <Link to="/cpus" className="back-button">
                    <IoIosArrowBack /> Voltar para a lista
                </Link>
                <h1>{cpu.manufacturer} {cpu.model}</h1>
            </header>

            <div className="detail-content">
                {/* Coluna da Esquerda: Especificações Técnicas */}
                <div className="detail-specs-column">
                    <div className="detail-icon-wrapper">
                        <ComponentIcon type="cpus" size={60} />
                    </div>
                    <h2>Especificações Técnicas</h2>
                    <ul className="spec-list">
                        <li><strong>Fabricante:</strong> {cpu.manufacturer}</li>
                        <li><strong>Modelo:</strong> {cpu.model}</li>
                        <li><strong>Soquete:</strong> {cpu.socket}</li>
                        <li><strong>Núcleos:</strong> {cpu.n_cores}</li>
                        <li><strong>Clock Base:</strong> {cpu.base_clock_speed} GHz</li>
                        <li><strong>Clock Boost:</strong> {cpu.boost_clock_speed} GHz</li>
                        <li><strong>Consumo (TDP):</strong> {cpu.consumption}W</li>
                        <li><strong>Gráfico Integrado:</strong> {cpu.integrated_gpu || 'Não possui'}</li>
                    </ul>
                </div>

                {/* Coluna da Direita: Ofertas de Preço */}
                <div className="detail-offers-column">
                    <h2>Ofertas Disponíveis</h2>
                    <div className="offers-container">
                        {offers.length > 0 ? (
                            offers.map(offer => (
                                <div key={offer.url} className="offer-card">
                                    <div className="offer-details">
                                        <span className="offer-source">{offer.source}</span>
                                        <span className="offer-price">R$ {parseFloat(offer.current_price).toFixed(2)}</span>
                                    </div>
                                    <a href={offer.url} target="_blank" rel="noopener noreferrer" className="offer-button">
                                        Ir para a loja
                                    </a>
                                </div>
                            ))
                        ) : (
                            <p>Nenhuma oferta encontrada no momento.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CPUDetail;