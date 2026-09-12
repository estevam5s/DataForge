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
# 'editor/' e um pacote declarado ('dataforge.editor', mapeado de
# 'editor/'): sem ele o 'pip install' falha com "package directory
# 'editor' does not exist" — e falha na CI, nao aqui, porque no
# repositorio a pasta existe.
#
# Nao e peso morto na imagem final: ela e multi-estagio, e o segundo
# estagio copia apenas o que foi instalado. A extensao vai junto porque
# 'dataforge editor' precisa dela — inclusive de dentro de um container,
# quando alguem monta o volume do editor.
COPY editor ./editor

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
