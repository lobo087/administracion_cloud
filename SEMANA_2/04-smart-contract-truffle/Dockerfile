FROM node:20-alpine

WORKDIR /app

RUN apk add --no-cache git python3 make g++

COPY package*.json ./
RUN npm install

COPY . .

CMD ["npx", "truffle", "compile"]
