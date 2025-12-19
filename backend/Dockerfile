FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (needed for psycopg)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static at build time
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD sh -c "\
python manage.py migrate && \
if [ \"$CREATE_SUPERUSER\" = \"True\" ]; then \
  python manage.py create_render_superuser; \
fi && \
gunicorn hrms.wsgi:application --bind 0.0.0.0:$PORT"

