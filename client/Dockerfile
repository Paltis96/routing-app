FROM node:lts-alpine as builder

# make the 'app' folder the current working directory
WORKDIR /app
COPY package*.json ./

RUN npm install

# Copy rest of the files
COPY . .


ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN echo "VITE_API_URL=${VITE_API_URL}"  > .env.production

RUN echo VITE_API_URL


# Build the project
RUN npm run build


# FROM devforth/spa-to-http:latest
# COPY --from=builder /app/dist/ .

FROM nginx:alpine as production-build
COPY ./nginx.conf /etc/nginx/nginx.conf

## Remove default nginx index page
RUN rm -rf /usr/share/nginx/html/*

# Copy from the stahg 1
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
ENTRYPOINT ["nginx", "-g", "daemon off;"]