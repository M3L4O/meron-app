import React from 'react';
// Importa o nosso novo componente de ícone
import ComponentIcon from './ComponentIcon'; 
import './ComponentList.css'; // O CSS principal continua a ser importado aqui

const renderSpecs = (item, type) => {
    // ... (esta função não precisa de alteração)
};

const ComponentCard = ({ item, type }) => {
    const volatileInfo = item.volatile_data && item.volatile_data.length > 0 ? item.volatile_data[0] : null;

    return (
        <div className="card">
            {/* --- MUDANÇA AQUI: Substituímos o container da imagem pelo container do ícone --- */}
            <div className="card-icon-container">
                <ComponentIcon type={type} />
            </div>

            <div className="card-content">
                <h3 className="card-title">{item.manufacturer} {item.model}</h3>
                
                {renderSpecs(item, type)}

                <p className="price">
                    {volatileInfo && volatileInfo.current_price
                        ? `R$ ${parseFloat(volatileInfo.current_price).toFixed(2)}`
                        : 'Preço indisponível'}
                </p>
                <p className={`availability ${volatileInfo && volatileInfo.current_availability ? 'in-stock' : 'out-of-stock'}`}>
                    {volatileInfo ? (volatileInfo.current_availability ? 'Em estoque' : '') : ''}
                </p>
            </div>
        </div>
    );
};

export default ComponentCard;