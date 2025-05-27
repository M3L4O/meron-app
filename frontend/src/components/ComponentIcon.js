import React from 'react';
// Importa os ícones que vamos usar da biblioteca react-icons
import { FaMicrochip, FaMemory, FaHdd, FaPlug } from 'react-icons/fa';
import { CgCreditCard } from "react-icons/cg";
import { BsMotherboardFill, BsDeviceSsdFill } from "react-icons/bs";

// Um componente simples que mapeia um tipo para um ícone
const ComponentIcon = ({ type, size = 40 }) => {
    // Usamos um switch para retornar o ícone correto
    switch (type) {
        case 'cpus':
            return <FaMicrochip size={size} />;
        case 'gpus':
            return <CgCreditCard size={size} />;
        case 'rams':
            return <FaMemory size={size} />;
        case 'motherboards':
            return <BsMotherboardFill size={size} />;
        case 'storages':
            // Poderíamos até diferenciar por tipo de storage se a 'item' fosse passada
            return <BsDeviceSsdFill size={size} />;
        case 'psus':
            return <FaPlug size={size} />;
        default:
            // Ícone padrão caso o tipo não seja reconhecido
            return <FaMicrochip size={size} />;
    }
};

export default ComponentIcon;