FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

# 依存関係ファイルをコピー
COPY pyproject.toml poetry.lock ./

# poetry設定を変更（仮想環境を作成しない）
RUN poetry config virtualenvs.create false

# 依存関係のインストール
RUN poetry install --no-dev --no-interaction --no-ansi

# アプリケーションのソースコードをコピー
COPY api/ ./api/

# 非root ユーザーを作成
RUN useradd -m appuser
USER appuser

ENV PYTHONPATH=/app
ENV PORT=8080
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT}