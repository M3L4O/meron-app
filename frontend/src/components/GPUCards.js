import React from 'react';
import { MdMonitor } from 'react-icons/md'; // Mantenha este import
import './GPUCards.css';

function GPUCards({ gpu }) {
  return (
    <li className="component-item-card gpu-card-override">
      <div className="card-title-group">
        <MdMonitor className="component-icon" />
        <h2>{gpu.model}</h2>
      </div>
      {gpu.price && <p><strong>Preço:</strong> R$ {parseFloat(gpu.price).toFixed(2).replace('.', ',')}</p>}
      {gpu.availability && <p><strong>Disponibilidade:</strong> {gpu.availability}</p>}
    </li>
  );
}

export default GPUCards;