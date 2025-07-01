
import React from 'react';
import './Home.css'; // Vamos criar este CSS também

function Home() {
  return (
    <div className="home-container">
      <header className="home-header">
        <h1>Bem-vindo ao Meron App!</h1>
        <p>Seu catálogo de componentes de computador.</p>
      </header>
      <main className="home-main">
        <section className="home-section">
          <h2>Descubra Componentes</h2>
          <p>Navegue pelo nosso extenso catálogo de CPUs, GPUs, Placas-Mãe e muito mais.</p>
          <a href="/cpus" className="home-button">Ver CPUs</a> {/* Link para a página de CPUs */}
        </section>
        <section className="home-section">
          <h2>Monte Seu PC</h2>
          <p>Em breve, ferramentas para te ajudar a montar a máquina perfeita!</p>
          {/* Você pode adicionar mais links ou funcionalidades aqui no futuro */}
        </section>
      </main>
    </div>
  );
}

export default Home;