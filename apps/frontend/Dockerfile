FROM node:20

WORKDIR /app

# Copia dependências primeiro para otimizar cache
COPY package.json .
COPY package-lock.json .

# Instala todas as dependências (incluindo devDependencies)
RUN npm config set strict-ssl false
RUN npm install

# Copia todo o restante da aplicação
COPY . .

EXPOSE 3000

# Se sua rede trava TLS (como na You.On), isso evita falhas em fetch
ENV NODE_TLS_REJECT_UNAUTHORIZED=0

CMD ["npm", "run", "dev"]
