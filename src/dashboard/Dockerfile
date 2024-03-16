FROM node:latest

WORKDIR /app

COPY package.json .
COPY package-lock.json .

RUN npm install

COPY . .

RUN npm run build

EXPOSE 4321

ENV HOST=0.0.0.0
ENV PORT=4321

CMD ["node","./dist/server/entry.mjs"]