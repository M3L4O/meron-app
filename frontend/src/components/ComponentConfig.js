import React from 'react';
import ComponentIcon from './ComponentIcon';

export const componentConfig = {

    cpus: {
        displayName: 'Processador',
        apiEndpoint: '/api/cpus/',
        listRoute: '/cpus',
        Icon: (props) => <ComponentIcon type="cpus" {...props} />,
        cardClassName: 'cpu-card-override',
        specs: [
            { label: 'Fabricante', key: 'manufacturer' },
            { label: 'Modelo', key: 'model' },
            { label: 'Soquete', key: 'socket' },
            { label: 'Núcleos', key: 'n_cores' },
            { label: 'Clock Base', key: 'base_clock_speed', formatter: (val) => `${val} GHz` },
            { label: 'Clock Boost', key: 'boost_clock_speed', formatter: (val) => `${val} GHz` },
            { label: 'Consumo (TDP)', key: 'consumption', formatter: (val) => `${val}W` },
            { label: 'Gráfico Integrado', key: 'integrated_gpu', formatter: (val) => val || 'Não possui' },
        ],
    },

    gpus: {
        displayName: 'Placa de Vídeo',
        apiEndpoint: '/api/gpus/',
        listRoute: '/gpus',
        Icon: (props) => <ComponentIcon type="gpus" {...props} />,
        cardClassName: 'gpu-card-override',
        specs: [
            { label: 'Fabricante', key: 'manufacturer' },
            { label: 'Modelo', key: 'model' },
            { label: 'Chipset', key: 'chipset' },
            { label: 'VRAM', key: 'vram', formatter: (val) => `${val} GB` },
            { label: 'Clock Base', key: 'base_clock_speed', formatter: (val) => `${val} MHz` },
            { label: 'Clock Boost', key: 'boost_clock_speed', formatter: (val) => `${val} MHz` },
            { label: 'Consumo (TDP)', key: 'consumption', formatter: (val) => `${val}W` },
        ],
    },
    motherboards: {
        displayName: 'Placa-Mãe',
        apiEndpoint: '/api/motherboards/',
        listRoute: '/motherboards',
        Icon: (props) => <ComponentIcon type="motherboards" {...props} />,
        cardClassName: 'motherboard-card-override',
        specs: [
            { label: 'Fabricante', key: 'manufacturer' },
            { label: 'Modelo', key: 'model' },
            { label: 'Soquete', key: 'socket' },
            { label: 'Formato (Tamanho)', key: 'board_size' },
            { label: 'Slots de RAM', key: 'n_ram_slots' },
            { label: 'Geração de Memória', key: 'memory_gen' },
            { label: 'Memória Máxima', key: 'memory_max', formatter: (val) => `${val} GB` },
            { label: 'Velocidades Suportadas', key: 'memory_speeds' },
            { label: 'Portas SATA', key: 'sata' },
            { label: 'Slots M.2', key: 'm2' },
            { label: 'Slots PCIe x1', key: 'pcie_x1' },
            { label: 'Slots PCIe x4', key: 'pcie_x4' },
            { label: 'Slots PCIe x8', key: 'pcie_x8' },
            { label: 'Slots PCIe x16', key: 'pcie_x16' },
            { label: 'Portas USB', key: 'usb' },
        ],
    },
    rams: {
        displayName: 'Memória RAM',
        apiEndpoint: '/api/rams/',
        listRoute: '/rams',
        Icon: (props) => <ComponentIcon type="rams" {...props} />,
        cardClassName: 'ram-card-override',

        specs: [
            { label: 'Fabricante', key: 'manufacturer' },
            { label: 'Modelo', key: 'model' },
            { label: 'Geração', key: 'generation' },
            { label: 'Tamanho', key: 'size', formatter: (val) => `${val} GB` },
            { label: 'Velocidade', key: 'speed', formatter: (val) => `${val} MHz` },
        ],
    },
    storages: {
        displayName: 'Armazenamento',
        apiEndpoint: '/api/storages/',
        listRoute: '/storages',
        Icon: (props) => <ComponentIcon type="storages" {...props} />,
        cardClassName: 'storage-card-override',

        specs: [
            { label: 'Fabricante', key: 'manufacturer' },
            { label: 'Modelo', key: 'model' },
            { label: 'Capacidade', key: 'capacity', formatter: (val) => `${val} GB` },
            { label: 'Interface', key: 'io' },
            { label: 'Tipo', key: 'is_hdd', formatter: (val) => (val ? 'HDD' : 'SSD') },
            // Renderiza o RPM apenas se for um HDD
            { label: 'RPM', key: 'rpm', formatter: (val) => `${val} RPM`, condition: (component) => component.is_hdd && component.rpm > 0 },
        ],
    },
    psus: {
        displayName: 'Fonte de Alimentação',
        apiEndpoint: '/api/psus/',
        listRoute: '/psus',
        cardClassName: 'psu-card-override',

        Icon: (props) => <ComponentIcon type="psus" {...props} />,
        specs: [
            { label: 'Fabricante', key: 'manufacturer' },
            { label: 'Modelo', key: 'model' },
            { label: 'Potência', key: 'power', formatter: (val) => `${val}W` },
            { label: 'Certificação', key: 'rate' },
        ],
    },
};