# 🚀 Meron App

Bem-vindo ao repositório `meron-app`! Este é um projeto full-stack que combina um backend Django REST Framework (com scraper, Celery e Redis) e um frontend React. Tudo é orquestrado e containerizado usando Docker Compose para facilitar o desenvolvimento e a implantação.

## ✨ Visão Geral do Projeto

O `meron-app` foi projetado para... (adicione aqui a sua descrição principal do projeto, ex: "ser uma plataforma para coletar, organizar e exibir informações sobre componentes de hardware de computador, como CPUs, GPUs, Motherboards, etc., permitindo aos usuários pesquisar e comparar especificações e preços.").

### 🎯 Principais Funcionalidades

* **Coleta de Dados:** Backend com scraper integrado (via Celery) para coletar informações de componentes de hardware.
* **Armazenamento de Dados:** Persistência de dados usando SQLite no backend Django.
* **APIs RESTful:** Backend que expõe dados dos componentes via APIs RESTful para consumo pelo frontend.
* **Processamento Assíncrono:** Uso de Celery e Redis para execução de tarefas em segundo plano (e.g., scraping de dados).
* **Interface Web Intuitiva:** Frontend React para visualização e interação com os dados.

## 🛠️ Tecnologias Utilizadas

### Backend (Django)
* **Python:** Linguagem de programação (versão 3.11).
* **Django:** Framework web.
* **Django REST Framework (DRF):** Para construção das APIs.
* **Celery:** Para processamento de tarefas assíncronas.
* **Redis:** Como broker de mensagens para o Celery.
* **SQLite:** Banco de dados simples baseado em arquivo.
* **`django-cors-headers`:** Para gerenciar requisições Cross-Origin do frontend.
* **`python-dotenv`:** Para gerenciamento de variáveis de ambiente.

### Frontend (React)
* **React:** Biblioteca JavaScript para construção da interface de usuário.
* **Nginx:** Servidor web para servir os arquivos estáticos do frontend em ambiente Docker.

### Orquestração
* **Docker:** Para containerização das aplicações.
* **Docker Compose:** Para definir e rodar a aplicação multi-container.

## 🚀 Primeiros Passos

Siga estas instruções para configurar e rodar o projeto em sua máquina local.

### Pré-requisitos

Certifique-se de ter os seguintes softwares instalados em seu sistema:

* [**Docker Desktop**](https://www.docker.com/products/docker-desktop/) (que inclui Docker Engine e Docker Compose)
* [**Git**](https://git-scm.com/downloads)

### Configuração e Instalação

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/m3l4o/meron-app.git
    cd meron-app
    ```

2.  **Configurar Variáveis de Ambiente:**
    * **Backend:** Crie o arquivo `.env` na pasta `backend/database/` e adicione as variáveis:
        **`meron-app/backend/database/.env`**
        ```
        SECRET_KEY=sua_chave_secreta_aqui # Gere uma chave segura
        DEBUG=True
        REDIS_HOST=redis
        REDIS_PORT=6379
        ```
        *Para `SECRET_KEY`, você pode gerar uma string aleatória longa. Em produção, garanta que esta chave seja muito segura.*

    * **Frontend (Desenvolvimento):** Crie o arquivo `.env.development` na pasta `frontend/` e adicione:
        **`meron-app/frontend/.env.development`**
        ```
        REACT_APP_DJANGO_API_URL=http://localhost:8000/api/
        ```

    * **Frontend (Produção/Docker Build):** Crie o arquivo `.env.production` na pasta `frontend/` e adicione:
        **`meron-app/frontend/.env.production`**
        ```
        REACT_APP_DJANGO_API_URL=http://backend:8000/api/
        ```

3.  **Construa as Imagens Docker:**
    A partir da raiz do repositório `meron-app/`:
    ```bash
    docker-compose build
    ```
    Este comando irá construir as imagens para o backend (Django) e frontend (React/Nginx), incluindo todas as dependências.

### Executando a Aplicação

Para iniciar todos os serviços da aplicação (backend Django, Celery Worker, Celery Beat, Redis e frontend React/Nginx):

A partir da raiz do repositório `meron-app/`:
```bash
docker-compose up
```

Após os containers subirem:

* **Backend (APIs):** Acessível em `http://localhost:8000/api/`
    * Exemplo: `http://localhost:8000/api/cpus/`
    * O admin do Django estará em `http://localhost:8000/admin/` (Você precisará criar um superusuário para acessá-lo: `docker-compose exec backend python manage.py createsuperuser`)
* **Frontend (Interface Web):** Acessível em `http://localhost:3000/`

**Importando Dados Iniciais (Opcional):**
O projeto inclui um comando para importar dados iniciais de componentes (CPUs, GPUs, etc.) a partir de arquivos `.json` na pasta `backend/data/`. Após o `docker-compose up` e com o backend rodando, você pode executar:
```bash
docker-compose exec backend python manage.py import_components
```

## 📂 Estrutura do Projeto

```
meron-app/
├── backend/                  # Projeto Django (API REST, Scraper, Celery)
│   ├── database/             # Configurações principais do Django
│   │   └── .env              # Variáveis de ambiente do backend
│   ├── scraper/              # Aplicação Django para scraper, modelos, APIs
│   ├── data/                 # Arquivos JSON de dados iniciais
│   ├── manage.py
│   ├── Dockerfile            # Dockerfile para o backend
│   └── requirements.txt
├── frontend/                 # Projeto React (Interface de Usuário)
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── .env.development      # Variáveis de ambiente para dev do frontend
│   ├── .env.production       # Variáveis de ambiente para build do frontend
│   ├── Dockerfile            # Dockerfile para o frontend
│   └── ...
└── docker-compose.yml        # Orquestração de todos os serviços Docker
```

## 🔑 API Endpoints (Principais)

O backend Django expõe os seguintes endpoints RESTful (ex: `http://localhost:8000/api/`):

* `/api/cpus/`
* `/api/gpus/`
* `/api/motherboards/`
* `/api/rams/`
* `/api/psus/`
* `/api/storages/`
* `/api/volatiles/`

Para detalhes sobre os campos e funcionalidades de cada endpoint, consulte os serializadores e views em `backend/scraper/serializers.py` e `backend/scraper/views.py`.

## 🤝 Contribuição

Sinta-se à vontade para contribuir com este projeto! Por favor, siga as diretrizes de Conventional Commits para suas mensagens de commit:

* `feat:` Para adição de uma nova funcionalidade
* `fix:` Para corrigir um bug
* `docs:` Alterações na documentação
* `style:` Alterações que não afetam o código (espaços, formatação, etc.)
* `refactor:` Mudanças no código que não corrigem bugs nem adicionam funcionalidades
* `test:` Adição ou correção de testes
* `chore:` Atualizações de tarefas de build, ferramentas de desenvolvimento, etc.