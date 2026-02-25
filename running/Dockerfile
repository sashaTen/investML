FROM python:3.12-slim

WORKDIR /application
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Copy requirements first (better caching)
COPY  reqs_run.txt  .


RUN pip  install --upgrade pip 
# Install dependencies
RUN pip install --no-cache-dir -r reqs_run.txt 


# Copy the rest of the app
COPY . .

# Expose the desired port
EXPOSE 8080

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080"]





