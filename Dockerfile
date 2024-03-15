# Use a base image with Ubuntu
FROM ubuntu:latest

# Update package lists
RUN apt-get update

# Install Python and pip
RUN apt-get install -y python3 python3-pip

# Copy your script into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Command to run the script
CMD ["python3", "dash_app.py"]