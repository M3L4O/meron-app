import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { IoIosArrowBack, IoIosArrowForward } from 'react-icons/io';
import GenericCardSkeleton from './GenericCardSkeleton';
import useSessionStorageState from '../hooks/useSessionStorageState';
import useWindowSize from '../hooks/useWindowSize';
import './ComponentList.css';

function useComponentApi(componentType, page, searchTerm, mockDataFunction) {
  const [data, setData] = useState({ items: [], total: 0, next: null, prev: null });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const debounceTimeout = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        if (searchTerm) params.append('search', searchTerm);
        if (page > 1) params.append('page', page);

        const response = await fetch(`/api/${componentType}/?${params.toString()}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const result = await response.json();
        const processedResults = mockDataFunction ? mockDataFunction(result.results) : result.results;

        setData({
          items: processedResults,
          total: result.count,
          next: result.next,
          prev: result.previous
        });
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }, 500);

    return () => clearTimeout(debounceTimeout);
  }, [componentType, page, searchTerm, mockDataFunction]);

  return { ...data, loading, error };
}

function ComponentList({ componentType, componentNamePlural, searchPlaceholder, renderItem, mockDataFunction }) {
  const [page, setPage] = useSessionStorageState(PAGE_NUMBER_KEY(componentType), 1);
  const [searchTerm, setSearchTerm] = useSessionStorageState(SEARCH_TERM_KEY(componentType), '');
  const { items, total, next, prev, loading, error } = useComponentApi(componentType, page, searchTerm, mockDataFunction);

  const { width } = useWindowSize();
  const isMobile = width <= 480;
  const listContainerRef = useRef(null);
  const pageSize = 50;
  const totalPages = Math.ceil(total / pageSize);

  const getPageNumbers = () => {
    const pageNumbers = [];
    const maxPagesToShow = 7;
    const ellipsis = '...';

    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) pageNumbers.push(i);
    } else {
      let startPage = Math.max(1, page - 3);
      let endPage = Math.min(totalPages, page + 3);

      if (startPage > 1) {
        pageNumbers.push(1);
        if (startPage > 2) pageNumbers.push(ellipsis);
      }

      for (let i = startPage; i <= endPage; i++) pageNumbers.push(i);

      if (endPage < totalPages) {
        if (endPage < totalPages - 1) pageNumbers.push(ellipsis);
        pageNumbers.push(totalPages);
      }
    }
    return pageNumbers;
  };

  const pageNumbers = getPageNumbers();

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setPage(1);
  };

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
            <p>Erro: {error.message}.</p>
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
                  to={`/component/${componentType}/${item.id}`}
                  key={item.id}
                  className="component-card-link"
                >
                  {renderItem(item)}
                </Link>
              ))
            ) : (
              <p>Nenhum(a) {componentNamePlural.toLowerCase().slice(0, -1)} encontrado(a).</p>
            )}
          </ul>
        )}

        {!loading && total > 0 && (
          <div className="pagination-controls">
            <button onClick={() => setPage(page - 1)} disabled={!prev}>
              <IoIosArrowBack /> Anterior
            </button>

            {!isMobile ? (
              pageNumbers.map((p, index) =>
                p === '...' ? (
                  <span key={index} className="pagination-ellipsis">...</span>
                ) : (
                  <button
                    key={p}
                    onClick={() => setPage(p)}
                    className={`page-number-button ${p === page ? 'active' : ''}`}
                  >
                    {p}
                  </button>
                )
              )
            ) : (
              <span className="current-page">Página {page} de {totalPages}</span>
            )}

            <button onClick={() => setPage(page + 1)} disabled={!next}>
              Próxima <IoIosArrowForward />
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

const PAGE_NUMBER_KEY = (type) => `${type}_pageNumber`;
const SEARCH_TERM_KEY = (type) => `${type}_searchTerm`;

export default ComponentList;
