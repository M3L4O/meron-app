# --- Estágio de Build (para construir o aplicativo React) ---
FROM node:18-alpine AS build

WORKDIR /app

# Copia package.json e package-lock.json para instalar dependências
# ATENÇÃO: Mudança de yarn.lock para package-lock.json
COPY package.json package-lock.json ./

# Instala as dependências do Node.js usando npm
# ATENÇÃO: Mudança de yarn install para npm install
RUN npm install --legacy-peer-deps

# Copia o restante do código do frontend
COPY . .

# Constrói o aplicativo React para produção usando npm
# ATENÇÃO: Mudança de yarn build para npm run build
RUN npm run build

# --- Estágio de Serviço (para servir os arquivos estáticos com Nginx) ---
FROM nginx:alpine

# Copia os arquivos de build do React do estágio 'build' para o diretório de serviço do Nginx
COPY --from=build /app/build /usr/share/nginx/html

# Expõe a porta padrão do Nginx
EXPOSE 80

# Comando para iniciar o Nginx
    CMD ["nginx", "-g", "daemon off;"]