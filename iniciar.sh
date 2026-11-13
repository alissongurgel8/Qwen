#!/bin/bash
# Script para iniciar a interface visual do Qwen Studio

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=========================================="
echo "🧠 Iniciando Qwen Studio..."
echo "=========================================="

# Verifica se o Ollama está respondendo
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama não está respondendo em http://localhost:11434."
    echo "💡 Caso necessário, inicie o serviço com: ollama serve"
else
    echo "✅ Ollama detectado e conectado com sucesso!"
fi

echo "🚀 Abrindo a aplicação no navegador (porta 8501)..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
