FROM python:3.11.10-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd -m user
WORKDIR /app

FROM base AS dependencies
COPY --chown=user:user requirements.txt ./
RUN python3 -m pip install -r requirements.txt

FROM dependencies AS development
COPY --chown=user:user . .
USER user
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

FROM dependencies as testing
COPY . ./
CMD ["python", "-m", "pytest", "-v", "--disable-warnings", "--maxfail=1"]