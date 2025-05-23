import React from 'react';
import { RiCpuLine } from 'react-icons/ri'; // Mantenha este import
import './CPUCards.css';

function CPUCards({ cpu }) {
  return (
    <li className="component-item-card cpu-card-override">
      <div className="card-title-group">
        <RiCpuLine className="component-icon" />
        <h2>{cpu.model}</h2>
      </div>
      {cpu.price && <p><strong>Preço:</strong> R$ {parseFloat(cpu.price).toFixed(2).replace('.', ',')}</p>}
      {cpu.availability && <p><strong>Disponibilidade:</strong> {cpu.availability}</p>}
    </li>
  );
}

export default CPUCards;