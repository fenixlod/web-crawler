# Dockerfile

# Start from the Python 3.10 image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt ./

# Install all requirements
RUN pip install -r requirements.txt

# Download and install pyppeteer cromium browser
RUN playwright install

# Download and install playwright dependancies
RUN playwright install-deps

EXPOSE 80