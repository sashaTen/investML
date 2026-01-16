# 1. Base image (Python runtime)
FROM python:3.11-slim


# 2. Set working directory inside container
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN pip install --upgrade pip
# 3. Copy dependency list first (important for caching)
COPY requirements.txt  /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN python - <<EOF
import nltk
nltk.download("punkt")
nltk.download("stopwords")
EOF
# 4. Install dependencies
COPY . /app/

# 5. Copy the rest of the code
EXPOSE 8000 

# 6. Default command (can be overridden)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

