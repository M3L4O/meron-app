import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { IoIosArrowBack, IoIosArrowForward } from 'react-icons/io';
import GenericCardSkeleton from './GenericCardSkeleton';
import './ComponentList.css';

// Chaves para sessionStorage
const PAGE_NUMBER_KEY = (type) => `${type}_pageNumber`;
const SEARCH_TERM_KEY = (type) => `${type}_searchTerm`;
const SCROLL_POS_KEY = (type) => `${type}_scrollPos`; // Usar para scroll, se persistir

function ComponentList({ 
    componentType, 
    componentNameSingular, 
    componentNamePlural, 
    searchPlaceholder, 
    renderItem, 
    mockDataFunction 
}) {
  const location = useLocation(); // Ainda útil para limpar estado se necessário
  const navigate = useNavigate();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [nextPage, setNextPage] = useState(null); 
  const [prevPage, setPrevPage] = useState(null);
  
  // 1. Inicializa o estado lendo do sessionStorage OU usa o padrão
  const [searchTerm, setSearchTerm] = useState(() => {
    return sessionStorage.getItem(SEARCH_TERM_KEY(componentType)) || '';
  });
  const [currentPageNumber, setCurrentPageNumber] = useState(() => {
    return parseInt(sessionStorage.getItem(PAGE_NUMBER_KEY(componentType)) || '1', 10);
  });
  
  const [totalItemsCount, setTotalItemsCount] = useState(0);

  const searchTimeoutRef = useRef(null);
  const listContainerRef = useRef(null); // Ref para o container da lista

  const ellipsis = '...';
  const pageSize = 10;

  const buildApiUrl = useCallback((page, term) => {
    const baseUrl = `http://localhost:8000/api/${componentType}/`;
    const params = [];

    if (term) {
      params.push(`search=${encodeURIComponent(term)}`);
    }
    if (page && page > 1) {
      params.push(`page=${page}`);
    }

    if (params.length > 0) {
      return `${baseUrl}?${params.join('&')}`;
    }
    return baseUrl;
  }, [componentType]);

  // useEffect para salvar o estado no sessionStorage sempre que searchTerm ou currentPageNumber mudarem
  useEffect(() => {
    sessionStorage.setItem(SEARCH_TERM_KEY(componentType), searchTerm);
    sessionStorage.setItem(PAGE_NUMBER_KEY(componentType), currentPageNumber.toString());
    // Salvamos a posição de rolagem ANTES de sair da página
    const handleBeforeUnload = () => {
      if (listContainerRef.current) {
        sessionStorage.setItem(SCROLL_POS_KEY(componentType), listContainerRef.current.scrollTop.toString());
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [searchTerm, currentPageNumber, componentType]);

  // useEffect para buscar os itens (único useEffect de fetch)
  useEffect(() => {
    if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
    }

    searchTimeoutRef.current = setTimeout(async () => {
        setLoading(true);
        setError(null);
        try {
            const urlToFetch = buildApiUrl(currentPageNumber, searchTerm);
            const response = await fetch(urlToFetch);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            const itemsWithMockedData = mockDataFunction ? mockDataFunction(data.results) : data.results;

            await new Promise(resolve => setTimeout(resolve, 1000)); // Atraso artificial

            setItems(itemsWithMockedData);
            setNextPage(data.next);
            setPrevPage(data.previous);
            setTotalItemsCount(data.count);

            // Restaurar a posição de rolagem após o fetch e setar os itens
            const storedScrollPos = sessionStorage.getItem(SCROLL_POS_KEY(componentType));
            if (listContainerRef.current && storedScrollPos) {
              listContainerRef.current.scrollTop = parseInt(storedScrollPos, 10);
              sessionStorage.removeItem(SCROLL_POS_KEY(componentType)); // Limpa após uso
            }

        } catch (err) {
            setError(err);
        } finally {
            setLoading(false);
        }
    }, 500); // Debounce de 500ms

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
    // Dependências: searchTerm, currentPageNumber, componentType, buildApiUrl, mockDataFunction
    // location.state e navigate NÃO são mais dependências diretas para o fetch
  }, [searchTerm, currentPageNumber, componentType, buildApiUrl, mockDataFunction]);


  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setCurrentPageNumber(1); // Sempre volta para a primeira página ao buscar
  };

  const goToPage = (pageNumber) => {
    setCurrentPageNumber(pageNumber);
  };

  const totalPages = Math.ceil(totalItemsCount / pageSize);

  const getPageNumbers = () => {
    const pageNumbers = [];
    const maxPagesToShow = 7; 

    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) {
        pageNumbers.push(i);
      }
    } else {
      const startPage = Math.max(1, currentPageNumber - Math.floor(maxPagesToShow / 2));
      const endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

      if (startPage > 1) {
        pageNumbers.push(1);
        if (startPage > 2) {
          pageNumbers.push(ellipsis);
        }
      }

      for (let i = startPage; i <= endPage; i++) {
        pageNumbers.push(i);
      }

      if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
          pageNumbers.push(ellipsis);
        }
        pageNumbers.push(totalPages);
      }
    }
    return pageNumbers;
  };

  const pageNumbers = getPageNumbers();

  return (
    <div className="component-list-container" ref={listContainerRef}>
      <header className="component-list-header">
        <h1>Catálogo de {componentNamePlural}</h1>
        <div className="search-bar">
          <input
            type="text"
            placeholder={searchPlaceholder}
            value={searchTerm}
            onChange={handleSearchChange}
          />
        </div>
      </header>
      <main>
        {error ? (
          <div className="error-message">
            <p>Erro: {error.message}. Por favor, verifique se o backend está rodando.</p>
            <Link to={`/${componentType}`} className="back-button">Tentar novamente</Link>
          </div>
        ) : (
          <ul className="component-list-grid">
            {loading ? (
              Array.from({ length: pageSize }).map((_, index) => (
                <GenericCardSkeleton key={index} />
              ))
            ) : items.length > 0 ? (
              items.map((item) => (
                <Link 
                  to={`/${componentType}/${item.id}`} 
                  key={item.id} 
                  className="component-item-link"
                  // Removido o state do Link, pois o estado é salvo no sessionStorage
                >
                  {renderItem(item)}
                </Link>
              ))
            ) : (
              <p>Nenhum(a) {componentNameSingular} encontrado(a) com os critérios de busca.</p>
            )}
          </ul>
        )}
        
        {!loading && (totalItemsCount > 0) && (
          <div className="pagination-controls">
            <button onClick={() => goToPage(currentPageNumber - 1)} disabled={currentPageNumber === 1}>
              <IoIosArrowBack className="pagination-icon" /> Anterior
            </button>
            
            {pageNumbers.map((p, index) => (
              p === ellipsis ? (
                <span key={index} className="pagination-ellipsis">...</span>
              ) : (
                <button 
                  key={p} 
                  onClick={() => goToPage(p)} 
                  className={`page-number-button ${p === currentPageNumber ? 'active' : ''}`}
                >
                  {p}
                </button>
              )
            ))}

            <button onClick={() => goToPage(currentPageNumber + 1)} disabled={currentPageNumber === totalPages || totalPages === 0}>
              Próxima <IoIosArrowForward className="pagination-icon" />
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default ComponentList;