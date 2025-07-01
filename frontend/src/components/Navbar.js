import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { FaBars, FaTimes } from 'react-icons/fa'; // Ícones para o menu hambúrguer
import './Navbar.css';

const Navbar = () => {
    // Estado para controlar se o menu móvel está aberto ou fechado
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    // Função para alternar o estado do menu
    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    // Função para fechar o menu ao clicar em um link (útil em mobile)
    const closeMenu = () => {
        setIsMenuOpen(false);
    };

    return (
        <nav className="navbar">
            <div className="navbar-container">
                {/* O logo/marca sempre leva para a página inicial */}
                <Link to="/" className="navbar-brand" onClick={closeMenu}>
                    Meron
                </Link>

                {/* Ícone do menu hambúrguer que aparece em telas pequenas */}
                <div className="menu-icon" onClick={toggleMenu}>
                    {isMenuOpen ? <FaTimes /> : <FaBars />}
                </div>

                {/* Lista de links de navegação */}
                {/* A classe 'active' é adicionada/removida com base no estado 'isMenuOpen' */}
                <ul className={isMenuOpen ? 'nav-menu active' : 'nav-menu'}>
                    <li className="nav-item">
                        <NavLink to="/cpus" className="nav-link" onClick={closeMenu}>
                            CPUs
                        </NavLink>
                    </li>
                    <li className="nav-item">
                        <NavLink to="/gpus" className="nav-link" onClick={closeMenu}>
                            GPUs
                        </NavLink>
                    </li>
                    <li className="nav-item">
                        <NavLink to="/motherboards" className="nav-link" onClick={closeMenu}>
                            Placas-Mãe
                        </NavLink>
                    </li>
                    <li className="nav-item">
                        <NavLink to="/rams" className="nav-link" onClick={closeMenu}>
                            RAM
                        </NavLink>
                    </li>
                    <li className="nav-item">
                        <NavLink to="/storages" className="nav-link" onClick={closeMenu}>
                            Armazenamento
                        </NavLink>
                    </li>
                    <li className="nav-item">
                        <NavLink to="/psus" className="nav-link" onClick={closeMenu}>
                            Fontes (PSU)
                        </NavLink>
                    </li>
                </ul>
            </div>
        </nav>
    );
};

export default Navbar;