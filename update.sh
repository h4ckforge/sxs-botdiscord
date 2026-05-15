#!/bin/bash
# ANNA Bot - Script de Update
# Uso: ./update.sh [version]
# Si no se especifica version, usa la última del remote

set -e

BOT_DIR="/opt/bot"  # Ajustar según tu instalación
SERVICE_NAME="anna-bot"

echo "🔄 Actualizando ANNA Bot..."

cd "$BOT_DIR"

# Fetch latest
echo "📥 Obteniendo cambios..."
git fetch --tags

if [ -z "$1" ]; then
    # Sin versión: checkout al último tag
    LATEST_TAG=$(git describe --tags --abbrev=0)
    echo "⬇️  Latest tag: $LATEST_TAG"
    git checkout "$LATEST_TAG"
else
    # Con versión: checkout al tag especificado
    echo "⬇️  checkout tags/v$1"
    git checkout "tags/v$1"
fi

# Actualizar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt -q

# Reiniciar servicio
echo "🔁 Reiniciando servicio..."
sudo systemctl restart "$SERVICE_NAME"

echo "✅ Update completado!"
echo "📋 Nueva versión: $(cat VERSION.txt)"