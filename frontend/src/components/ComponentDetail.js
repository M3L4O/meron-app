import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { IoIosArrowBack } from 'react-icons/io';
import { componentConfig } from './ComponentConfig';
import './ComponentDetail.css'; // Arquivo de CSS unificado para os cards

const ComponentDetail = () => {
    const { componentType, id } = useParams();
    const navigate = useNavigate();
    const config = componentConfig[componentType];

    const [component, setComponent] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!config) {
            console.error(`Configuração para o tipo "${componentType}" não encontrada.`);
            navigate('/not-found');
            return;
        }

        const fetchDetails = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`${config.apiEndpoint}${id}/`);
                if (!response.ok) {
                    throw new Error(`Erro HTTP! Status: ${response.status}`);
                }
                const data = await response.json();
                setComponent(data);
            } catch (err) {
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        fetchDetails();
    }, [componentType, id, config, navigate]);

    if (!config) return null;
    if (loading) return <div className="detail-container loading">A carregar detalhes...</div>;

    if (error) {
        return (
            <div className="detail-container error">
                <h2>Erro ao Carregar</h2>
                <p>{error.message}</p>
                <Link to={config.listRoute} className="back-button">
                    <IoIosArrowBack /> Voltar para a lista de {config.displayName.toLowerCase()}s
                </Link>
            </div>
        );
    }

    if (!component) return <div className="detail-container"><h2>{config.displayName} não encontrado.</h2></div>;

    const isOfferAvailable = (offer) => offer.current_availability || parseFloat(offer.current_price) > 0;
    const getCardClassBySource = (source) => {
        const sourceName = source.toLowerCase();
        if (sourceName.includes('kabum')) return 'offer-card--kabum';
        if (sourceName.includes('pichau')) return 'offer-card--pichau';
        return '';
    };

    const { Icon } = config;
    const offers = component.volatile_data || [];

    return (
        <div className="detail-container">
            <header className="detail-header">
                <Link to={config.listRoute} className="back-button">
                    <IoIosArrowBack /> Voltar para a lista
                </Link>
                <h1>{component.manufacturer} {component.model}</h1>
            </header>

            <div className="detail-content">
                <div className="detail-specs-column">
                    <div className="detail-icon-wrapper">
                        <Icon size={60} />
                    </div>
                    <h2>Especificações Técnicas</h2>
                    <ul className="spec-list">
                        {config.specs.map(spec => {
                            const value = component[spec.key];
                            const shouldRender = spec.condition ? spec.condition(component) : (value !== null && value !== undefined && value !== '');

                            return shouldRender && (
                                <li key={spec.key}>
                                    <strong>{spec.label}:</strong>
                                    {spec.formatter ? spec.formatter(value) : value}
                                </li>
                            );
                        })}
                    </ul>
                </div>

                <div className="detail-offers-column">
                    <h2>Ofertas Disponíveis</h2>
                    <div className="offers-container">
                        {offers.length > 0 ? (
                            offers.map((offer, idx) => (
                                <div key={offer.url + idx} className={`offer-card ${getCardClassBySource(offer.source)}`}>
                                    <div className="offer-details">
                                        <span className="offer-source">{offer.source}</span>
                                        {isOfferAvailable(offer) ? (
                                            <span className="offer-price">
                                                R$ {parseFloat(offer.current_price).toFixed(2)}
                                            </span>
                                        ) : (
                                            <span className="offer-unavailable">Produto indisponível</span>
                                        )}
                                    </div>
                                    {(
                                        <a href={offer.url} target="_blank" rel="noopener noreferrer" className="offer-button">
                                            Ir para a loja
                                        </a>
                                    )}
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

export default ComponentDetail;