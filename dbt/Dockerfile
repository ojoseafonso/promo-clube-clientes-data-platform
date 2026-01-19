# Usando uma imagem base com Python
FROM python:3.11-slim

# Definindo o mantenedor
LABEL maintainer="Proj_Promo_V2"

# Atualizando a lista de pacotes e instalando dependências
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    vim \
    nano \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar a pasta /iac como um ponto de montagem para um volume
RUN mkdir /workspace
VOLUME /worskspace

# Criando um diretório de trabalho
WORKDIR /workspace

# Instalando DBT e adaptador para o sqlite
RUN pip install dbt-core==1.9.1
RUN pip install dbt-snowflake==1.9.1

# Expor a porta
EXPOSE 8080 3333

# Definir o comando padrão para execução quando o container for iniciado
CMD ["/bin/bash"]
