# DataForge — imagem oficial
#
#   docker run --rm -it estevan5s/dataforge repl
#   docker run --rm -v "$PWD:/app" estevan5s/dataforge run main.df
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
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.documentation="https://dataforge-lang.vercel.app/docs"
LABEL org.opencontainers.image.source="https://github.com/estevam5s/DataForge"

COPY --from=construcao /instalado /usr/local

# Usuário sem privilégio: um .df não deveria rodar como root
RUN useradd --create-home --shell /bin/bash forge
USER forge
WORKDIR /app

# 'run' sem argumento usa a entrada do forge.toml, então o padrão é útil
ENTRYPOINT ["dataforge"]
CMD ["repl"]
