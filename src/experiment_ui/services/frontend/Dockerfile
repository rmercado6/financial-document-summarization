FROM node:lts-alpine

LABEL version=0.0.0

ARG SEARCH_API_URL

WORKDIR /app

COPY package.json .

RUN npm install

RUN echo "VITE_SEARCH_API_URL=${SEARCH_API_URL}" > .env

COPY . .

RUN npm run build

EXPOSE ${PORT}

CMD [ "npm", "run", "dev" ]
