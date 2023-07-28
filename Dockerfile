# Use Python 3.9-slim as the base image - reduced in size
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the necessary files into the container
COPY input_molecules.txt compound_normalization.py requirements.txt /app/

# Install required dependencies
RUN pip install -r requirements.txt

# Call python script with argument
CMD [ "python", "./compound_normalization.py", "input_molecules.txt" ]