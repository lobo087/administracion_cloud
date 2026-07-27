FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY hardhat.config.ts tsconfig.json ./
COPY contracts/ contracts/
COPY scripts/ scripts/

RUN npx hardhat compile

CMD ["npx", "hardhat", "run", "scripts/deploy-registro-evidencias.ts", "--network", "redForense"]
