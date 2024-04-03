# build env
FROM node:13.12.0-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build
COPY redoc.html build/
COPY openapi-schema.yml build/
CMD cp -r build/. /frontend_static/
