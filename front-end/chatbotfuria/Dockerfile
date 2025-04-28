FROM node:20-slim

WORKDIR /app

COPY . .

RUN npm install

RUN rm -rf node_modules package-lock.json && npm install

