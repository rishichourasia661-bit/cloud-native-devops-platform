FROM node:24-alpine

WORKDIR /app

COPY app/package*.json ./

RUN npm install --global npm@11.21.1 \
    && npm ci --omit=dev

COPY app/ .

USER node

EXPOSE 3000

CMD ["node", "server.js"]