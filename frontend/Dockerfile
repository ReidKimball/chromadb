# Stage 1: Build the application
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Accept a build-time argument for the API URL
# --build-arg NEXT_PUBLIC_API_URL=https://wsdemo-backend-165871915889.us-central1.run.app
ARG NEXT_PUBLIC_API_URL
# Set it as an environment variable for the build process
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production image
FROM node:20-alpine AS runner

# Set working directory
WORKDIR /app

# Set environment variables
ENV NODE_ENV=production
# Uncomment the following line in case you want to disable telemetry during runtime.
# ENV NEXT_TELEMETRY_DISABLED 1

# Copy the standalone output from the builder stage
COPY --from=builder /app/.next/standalone ./
# Copy the public folder
COPY --from=builder /app/public ./public
# Copy the static assets
COPY --from=builder /app/.next/static ./.next/static

# Expose the port the app runs on
EXPOSE 3000

# Start the app
CMD ["node", "server.js"]
