FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/src
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir '.[dev]'
COPY alembic.ini ./
COPY migrations ./migrations
COPY tests ./tests
RUN useradd --create-home --uid 10001 appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "seekerlab.main:app", "--host", "0.0.0.0", "--port", "8000"]
