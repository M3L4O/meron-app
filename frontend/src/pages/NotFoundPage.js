import React from 'react';
import { Link } from 'react-router-dom';
import { FaGhost } from 'react-icons/fa'; // Um ícone divertido para a ocasião
import './NotFoundPage.css';

const NotFoundPage = () => {
    return (
        <div className="not-found-container">
            <FaGhost className="not-found-icon" />
            <h1 className="not-found-title">404</h1>
            <h2 className="not-found-subtitle">Página Não Encontrada</h2>
            <p className="not-found-text">
                Oops! A página que você está procurando não existe ou foi movida para outro lugar.
            </p>
            <Link to="/" className="not-found-button">
                Voltar para a Página Inicial
            </Link>
        </div>
    );
};

export default NotFoundPage;