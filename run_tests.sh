#!/bin/bash

echo "🚀 Rodando testes automatizados do You.On Intelligence..."
echo "📦 Ambiente: $(which python)"
echo "📁 Diretório atual: $(pwd)"
echo ""

# Ativa variáveis do .env se necessário
export $(grep -v '^#' .env | xargs)

# Roda testes com Pytest
pytest tests/ --maxfail=3 --disable-warnings -v

STATUS=$?

echo ""
if [ $STATUS -eq 0 ]; then
    echo "✅ TODOS OS TESTES PASSARAM"
else
    echo "❌ ALGUNS TESTES FALHARAM (status $STATUS)"
fi

exit $STATUS
