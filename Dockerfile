# Use Python 3.9-slim as the base image - reduced in size
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the necessary files into the container
COPY input_molecules.txt compound_normalization.py requirements.txt compounds_ranking.py run_scripts.py /app/

# Install required dependencies
RUN pip install -r requirements.txt

RUN chmod +x run_scripts.py
# Call python scripts
CMD [ "python3", "./run_scripts.py" ]