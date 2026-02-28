# syntax=docker/dockerfile:1
# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY reqs.txt .
RUN pip install --no-cache-dir -r reqs.txt

# create nltk folder
RUN mkdir -p /usr/local/nltk_data

# download nltk data INTO known folder
RUN python -m nltk.downloader \
-d /usr/local/nltk_data \
punkt punkt_tab stopwords wordnet

# tell python where nltk data lives
ENV NLTK_DATA=/usr/local/nltk_data
# Copy the rest of the application code into the container
COPY . .

# Define the command to run the application when the container starts
CMD ["python", "./retrain.py"]
