#!/bin/bash
set -e

echo "🚀 Instalando Airbyte Local..."

if ! command -v abctl &> /dev/null
then
  echo "⬇️ Instalando abctl..."
  curl -LsfS https://get.airbyte.com | bash
fi

echo "📦 Subindo Airbyte Local..."
abctl local install

echo "🌐 Airbyte disponível em: http://localhost:8080"
