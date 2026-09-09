# Frontend — Vite dev server (kept as dev server, not a production build,
# so the demo behaves exactly like `npm run dev` locally: fast, no separate
# static host needed for a 24-hour hackathon).
FROM node:20-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 5173

# --host so the dev server accepts connections from outside the container;
# VITE_API_BASE_URL / VITE_DEFAULT_EVENT_ID come from docker-compose.yml's
# environment: block (Vite reads any VITE_-prefixed process env var at
# dev-server startup, no .env file needed inside the container).
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
