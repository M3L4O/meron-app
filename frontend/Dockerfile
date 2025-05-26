# frontend/Dockerfile
# --- STAGE 1: Development environment for React ---
    FROM node:20-alpine

    # Set the working directory inside the container
    WORKDIR /app
    
    # Copy package.json and package-lock.json first
    COPY package.json ./
    COPY package-lock.json ./
    
    # Install Node.js dependencies
    RUN npm install
    
    # Copy the rest of the application source code
    COPY . .
    
    # Expose the port that Create React App's development server runs on (default 3000)
    EXPOSE 3000
    
    # Command to run the React development server
    # `npm start` by default runs on port 3000
    CMD ["npm", "start"]