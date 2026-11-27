FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Par défaut le site joint l'API par son propre relais (next.config.mjs, même adresse que le site) : le navigateur
# n'a qu'une adresse à connaître. L'adresse interne de l'API est figée à la construction.
ARG NEXT_PUBLIC_API_URL=""
ARG DALIL_API_INTERNAL=http://api:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL DALIL_API_INTERNAL=$DALIL_API_INTERNAL NEXT_TELEMETRY_DISABLED=1
RUN npx next build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
