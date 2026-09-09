# Backend — FastAPI + the trained crowd-prediction models
FROM python:3.12-slim

WORKDIR /app

# System deps needed by psycopg2-binary's runtime libs and scientific
# Python packages (numpy/scipy/scikit-learn wheels still want libgomp).
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Installed first, separately, so dependency layers cache across code edits.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# backend/data (ML models + dataset) is also mounted as a volume in
# docker-compose.yml, but it's copied here too so the image still works if
# run standalone without that volume.

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
