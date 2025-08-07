# Use an official Python runtime as a parent image
FROM python:3.13.5-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code to the working directory
COPY . .

# Copy the entrypoint script and make it executable
COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh

# Expose the port the app runs on
EXPOSE 8080

# Run the application using the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
