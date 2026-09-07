# DataForge — imagem oficial
#
#   docker run --rm -it dataforge/dataforge repl
#   docker run --rm -v "$PWD:/app" dataforge/dataforge run main.df
#
# Duas etapas para a imagem final não carregar as ferramentas de build.

FROM python:3.12-slim AS construcao

WORKDIR /fonte
COPY pyproject.toml README.md ./
COPY dataforge ./dataforge

# --no-cache-dir: a camada não guarda o cache do pip
RUN pip install --no-cache-dir --upgrade pip build \
 && pip install --no-cache-dir --prefix=/instalado .


FROM python:3.12-slim

LABEL org.opencontainers.image.title="DataForge"
LABEL org.opencontainers.image.description="Linguagem de programação interpretada, com vocabulário próprio"
LABEL org.opencontainers.image.version="4.1.0"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.documentation="https://dataforge-lang.vercel.app/docs"

COPY --from=construcao /instalado /usr/local

# Usuário sem privilégio: um .df não deveria rodar como root
RUN useradd --create-home --shell /bin/bash forge
USER forge
WORKDIR /app

# 'run' sem argumento usa a entrada do forge.toml, então o padrão é útil
ENTRYPOINT ["dataforge"]
CMD ["repl"]
