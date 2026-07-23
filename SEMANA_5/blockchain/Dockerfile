FROM node:22-alpine

WORKDIR /app

#RUN apk add --no-cache git python3 make g++

COPY package*.json ./
RUN npm install

COPY hardhat.config.ts tsconfig.json ./
COPY contracts/ contracts/
COPY scripts/ scripts/
COPY test/ test/

#CMD ["npx", "hardhat", "run", "scripts/crear-titulo.ts"]
CMD ["npx", "hardhat", "compile"]