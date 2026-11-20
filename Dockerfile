# Research prototype only — no auth or PHI protections; do not expose to the public Internet.
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY clinor ./clinor
RUN python -m pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn", "clinor.api:app", "--host", "0.0.0.0", "--port", "8000"]
