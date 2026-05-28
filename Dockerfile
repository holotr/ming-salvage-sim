FROM node:22-slim AS web-build

WORKDIR /app/web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MING_SIM_AUTH_DB=/app/data/app_auth.db \
    MING_SIM_SESSION_DAYS=7

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --home-dir /app app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY content ./content
COPY ming_sim ./ming_sim
COPY .agno_skills ./.agno_skills
COPY web_app.py ./
COPY docker-entrypoint.py ./
COPY --from=web-build /app/web/dist ./web/dist

RUN mkdir -p /app/data \
    && chown -R app:app /app

EXPOSE 8010

ENTRYPOINT ["python", "/app/docker-entrypoint.py"]
CMD ["python", "-m", "uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "8010"]
