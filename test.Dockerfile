# Python образ с предустановленным uv
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS base

# Размещение проекта в `/app`- директории
WORKDIR /app

# Установка сторонних зависимостей
RUN apt update \
    && apt install media-types procps --yes \
    && apt clean && apt autoclean && apt autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

# Установка python-зависимостей
COPY ./pyproject.toml ./uv.lock ./

RUN uv sync --compile-bytecode --locked --no-cache --no-install-project

COPY ./serializer ./serializer
COPY ./tests ./tests

ENTRYPOINT ["uv", "run", "pytest", "-vs", "--color=yes"]