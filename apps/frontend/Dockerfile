FROM node:20

WORKDIR /app

# Primeiro copia só o package.json e instala dependências
COPY package.json .
COPY package-lock.json .

RUN npm install

# Instala as ferramentas de build do CSS (DevDependencies)
RUN npm install --save-dev tailwindcss postcss autoprefixer

# Agora copia todo o resto
COPY . .

EXPOSE 3000

ENV NODE_TLS_REJECT_UNAUTHORIZED=0

CMD ["npm", "run", "dev"]
