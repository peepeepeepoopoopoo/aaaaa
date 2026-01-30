#!/bin/bash
# Script para crear instancia en vast.ai con PyTorch
# Uso: ./vastai_setup.sh <API_KEY>

API_KEY="${1:-}"

if [ -z "$API_KEY" ]; then
    echo "Uso: ./vastai_setup.sh <TU_API_KEY>"
    echo "Obtén tu API key en: https://cloud.vast.ai/account/"
    exit 1
fi

BASE_URL="https://cloud.vast.ai/api/v0"

echo "=== Buscando GPUs disponibles con >= 320GB de almacenamiento ==="

# Buscar ofertas de GPU ordenadas por precio
# disk_space >= 320, rentable=true
OFFERS=$(curl -k -s -H "Authorization: Bearer $API_KEY" \
    "$BASE_URL/bundles?q={\"rentable\":true,\"disk_space\":{\"gte\":320},\"order\":[[\"dph_total\",\"asc\"]],\"type\":\"on-demand\"}" 2>&1)

if echo "$OFFERS" | grep -q "error"; then
    echo "Error al buscar ofertas:"
    echo "$OFFERS" | head -20
    exit 1
fi

# Mostrar las 5 mejores ofertas
echo ""
echo "=== Top 5 ofertas más baratas ==="
echo "$OFFERS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
offers = data.get('offers', [])[:5]
for i, o in enumerate(offers, 1):
    print(f\"{i}. ID: {o['id']} | GPU: {o.get('gpu_name', 'N/A')} | VRAM: {o.get('gpu_ram', 0)/1024:.0f}GB | Disk: {o.get('disk_space', 0):.0f}GB | \$/hr: {o.get('dph_total', 0):.3f}\")
if offers:
    print(f\"\\nPara crear instancia con la primera oferta, usa el ID: {offers[0]['id']}\")
"

# Preguntar si quiere continuar
echo ""
read -p "¿Ingresa el OFFER_ID que quieres usar (o Enter para el primero): " OFFER_ID

if [ -z "$OFFER_ID" ]; then
    OFFER_ID=$(echo "$OFFERS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('offers', [{}])[0].get('id', ''))")
fi

if [ -z "$OFFER_ID" ]; then
    echo "No se encontraron ofertas disponibles"
    exit 1
fi

echo ""
echo "=== Creando volumen de 320GB ==="
# Primero obtener data centers disponibles
VOLUME_RESULT=$(curl -k -s -X POST -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"size": 320}' \
    "$BASE_URL/volumes/" 2>&1)

echo "Resultado volumen: $VOLUME_RESULT"
VOLUME_ID=$(echo "$VOLUME_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', data.get('volume_id', '')))" 2>/dev/null)

echo ""
echo "=== Creando instancia con OFFER_ID: $OFFER_ID ==="

# Crear la instancia
INSTANCE_RESULT=$(curl -k -s -X PUT -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
        \"client_id\": \"me\",
        \"image\": \"vastai/pytorch:@vastai-automatic-tag\",
        \"env\": {
            \"OPEN_BUTTON_PORT\": \"1111\",
            \"OPEN_BUTTON_TOKEN\": \"1\",
            \"JUPYTER_DIR\": \"/\",
            \"DATA_DIRECTORY\": \"/workspace/\",
            \"PORTAL_CONFIG\": \"localhost:1111:11111:/:Instance Portal|localhost:8080:18080:/:Jupyter|localhost:8080:8080:/terminals/1:Jupyter Terminal|localhost:8384:18384:/:Syncthing|localhost:6006:16006:/:Tensorboard\"
        },
        \"onstart\": \"entrypoint.sh\",
        \"disk\": 30,
        \"jupyter\": true,
        \"ssh\": true,
        \"direct\": true
    }" \
    "$BASE_URL/asks/$OFFER_ID/" 2>&1)

echo "Resultado: $INSTANCE_RESULT"

echo ""
echo "=== Proceso completado ==="
echo "Revisa tu dashboard en: https://cloud.vast.ai/instances/"
