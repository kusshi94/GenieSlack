FROM node:18-buster
RUN npm install -g gatsby-cli
WORKDIR /app
CMD ["/bin/bash", "-c", "gatsby clean && npm run build && gatsby serve"]
