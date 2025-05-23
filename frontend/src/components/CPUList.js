import React from 'react';
import ComponentList from './ComponentList'; // Importe o componente genérico
import CPUCards from './CPUCards'; // Importe o componente de renderização do card de CPU

// Função auxiliar para "mocar" (simular) preço e disponibilidade para CPUs
const mockPriceAndAvailabilityCPU = (cpus) => {
  const availabilityOptions = ['Disponível', 'Indisponível'];
  return cpus.map(cpu => ({
    ...cpu,
    price: (Math.random() * (4500 - 500) + 500).toFixed(2),
    availability: availabilityOptions[Math.floor(Math.random() * availabilityOptions.length)]
  }));
};

function CPUList() {
  // A função renderItem agora recebe o item e retorna o componente de card
  const renderCPUItem = (cpu) => <CPUCards cpu={cpu} />;

  return (
    <ComponentList
      componentType="cpus"
      componentNameSingular="CPU"
      componentNamePlural="CPUs"
      searchPlaceholder="Buscar CPUs por modelo, socket, etc."
      renderItem={renderCPUItem} // Passa a função de renderização do card
      mockDataFunction={mockPriceAndAvailabilityCPU}
    />
  );
}

export default CPUList;