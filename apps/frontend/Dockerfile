FROM node:20

WORKDIR /app

# Copia apenas as dependências para aproveitar cache
COPY package.json .
COPY package-lock.json .

# Instala as dependências do projeto
RUN npm config set strict-ssl false
RUN npm install

# Copia o restante da aplicação
COPY . .

# Expõe a porta padrão do Next.js
EXPOSE 3000

# Desativa verificação de TLS em ambientes corporativos como o da You.On
ENV NODE_TLS_REJECT_UNAUTHORIZED=0

# Comando padrão
CMD ["npm", "run", "dev"]
