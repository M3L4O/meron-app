import { Link } from 'react-router-dom';
import './ComponentCard.css'; // Arquivo de CSS unificado para os cards
import { componentConfig } from './ComponentConfig';

/**
 * Card genérico para exibir um item em uma lista de componentes.
 * O card inteiro funciona como um link para a página de detalhes.
 * * @param {object} component - O objeto de dados da peça (ex: um objeto cpu, gpu).
 * @param {string} componentType - A chave do tipo de componente (ex: 'cpus', 'gpus').
 */
const ComponentCard = ({ component, componentType }) => {
    // Busca a configuração apropriada para o tipo de componente
    const config = componentConfig[componentType];

    // Medida de segurança: se a configuração não for encontrada, não renderiza nada.
    if (!config) {
        console.error(`Configuração para o tipo "${componentType}" não encontrada.`);
        return null;
    }

    // Pega o Ícone e a classe CSS específica da configuração
    const { Icon, cardClassName } = config;

    // Lógica para extrair dados que podem ter nomes diferentes (ex: best_price ou price)
    const price = component.price || component.best_price;
    const availability = component.availability;

    return (
        // O card inteiro é um link para a página de detalhes genérica
        <Link to={`/component/${componentType}/${component.id}`} className="component-card-link">
            <li className={`component-item-card ${cardClassName || ''}`}>
                <div className="card-title-group">
                    {/* Renderiza o ícone dinamicamente a partir da configuração */}
                    <Icon className="component-icon" />
                    <h2>{component.manufacturer} {component.model}</h2>
                </div>
                <div className="card-info-group">
                    {/* Renderiza o preço somente se ele existir */}
                    {price && (
                        <p className="card-price">
                            R$ {parseFloat(price).toFixed(2).replace('.', ',')}
                        </p>
                    )}
                    {/* Renderiza a disponibilidade se ela existir */}
                    {availability && (
                        <p className="card-availability">
                            {availability}
                        </p>
                    )}
                </div>
            </li>
        </Link>
    );
};

export default ComponentCard;