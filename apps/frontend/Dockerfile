FROM node:20

WORKDIR /app

# Copia os arquivos de dependência do próprio contexto
COPY package.json ./
COPY package-lock.json ./

RUN npm config set strict-ssl false
RUN npm install

# Copia o restante do frontend (lembrando: já está dentro de apps/frontend)
COPY . .

EXPOSE 3000

ENV NODE_TLS_REJECT_UNAUTHORIZED=0

CMD ["npm", "run", "dev"]
