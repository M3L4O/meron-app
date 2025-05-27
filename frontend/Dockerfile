# frontend/Dockerfile

# ---- Estágio 1: Build da Aplicação React ----
FROM node:18-alpine AS builder

# Define o diretório de trabalho
WORKDIR /app

# Copia os ficheiros de manifesto de pacotes e instala as dependências
# Isso aproveita o cache do Docker, reinstalando as dependências apenas se o package.json mudar
COPY package.json package-lock.json ./
RUN npm install

# Copia o resto do código da aplicação
COPY . .

# Gera os ficheiros estáticos de produção
RUN npm run build


# ---- Estágio 2: Servir os ficheiros com Nginx ----
FROM nginx:stable-alpine

# Copia os ficheiros estáticos gerados no estágio anterior para o diretório web do Nginx
COPY --from=builder /app/build /usr/share/nginx/html

# Copia o ficheiro de configuração customizado do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expõe a porta 80 (padrão do Nginx)
EXPOSE 80

# Comando para iniciar o Nginx quando o contentor arrancar
CMD ["nginx", "-g", "daemon off;"]