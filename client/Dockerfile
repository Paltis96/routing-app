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

# Build the project
RUN npm run build


FROM devforth/spa-to-http:latest
COPY --from=builder /app/dist/ .
