import React from 'react';
import './GenericCardSkeleton.css'; // Vamos criar este CSS

function GenericCardSkeleton() {
  return (
    <li className="generic-skeleton-item">
      <div className="skeleton-line skeleton-line-large"></div> {/* Título/Modelo */}
      <div className="skeleton-line skeleton-line-medium"></div> {/* Preço */}
      <div className="skeleton-line skeleton-line-small"></div> {/* Disponibilidade */}
    </li>
  );
}

export default GenericCardSkeleton;