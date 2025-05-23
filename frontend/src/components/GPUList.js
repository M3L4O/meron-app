import React from 'react';
import ComponentList from './ComponentList'; // Use o componente genérico
import GPUCards from './GPUCards'; // Importe o componente de renderização do card de GPU

// Função auxiliar para "mocar" (simular) preço e disponibilidade para GPUs
const mockPriceAndAvailabilityGPU = (gpus) => {
  const availabilityOptions = ['Disponível', 'Indisponível'];
  return gpus.map(gpu => ({
    ...gpu,
    price: (Math.random() * (7000 - 1000) + 1000).toFixed(2), // Preços diferentes para GPUs
    availability: availabilityOptions[Math.floor(Math.random() * availabilityOptions.length)]
  }));
};

function GPUList() {
  // A função renderItem agora recebe o item e retorna o componente de card
  const renderGPUItem = (gpu) => <GPUCards gpu={gpu} />;

  return (
    <ComponentList
      componentType="gpus"
      componentNameSingular="GPU"
      componentNamePlural="GPUs"
      searchPlaceholder="Buscar GPUs por modelo, chipset, etc."
      renderItem={renderGPUItem} // Passa a função de renderização do card
      mockDataFunction={mockPriceAndAvailabilityGPU}
    />
  );
}

export default GPUList;