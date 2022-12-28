FROM node:lts-bullseye

WORKDIR /usr/src/app
COPY . /usr/src/app/
COPY package*.json ./
RUN npm install
RUN npm install axios

EXPOSE 3000

CMD ["npm", "run", "start"]
