#!/usr/bin/env python3
"""
Script para crear instancia en vast.ai con volumen persistente de 320GB
"""

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = "431745a46212b69187d8bdab52d5d7f368ad84c74693de168e7dc0a15d18d68f"
BASE_URL = "https://console.vast.ai/api/v0"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def buscar_ofertas():
    """Busca GPUs disponibles ordenadas por precio"""
    print("\n=== Buscando GPUs disponibles ===\n")

    response = requests.get(f"{BASE_URL}/bundles/", headers=HEADERS, verify=False)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []

    data = response.json()
    todas = data.get("offers", [])

    # Solo rentables con volume ask disponible, ordenadas por precio
    ofertas = [o for o in todas if o.get("rentable", False) and o.get("avail_vol_ask_id")]
    ofertas.sort(key=lambda x: x.get("dph_total", 999))

    print(f"Encontradas {len(ofertas)} ofertas con volumen disponible\n")
    print("-" * 80)
    print(f"{'#':<3} {'ID':<10} {'GPU':<22} {'VRAM':<8} {'$/hr':<10} {'VOL_ASK_ID':<12}")
    print("-" * 80)

    for i, o in enumerate(ofertas[:15], 1):
        gpu_name = o.get('gpu_name', 'N/A')[:21]
        vram = o.get('gpu_ram', 0) / 1024
        price = o.get('dph_total', 0)
        offer_id = o.get('id', 'N/A')
        vol_ask = o.get('avail_vol_ask_id', 'N/A')
        print(f"{i:<3} {offer_id:<10} {gpu_name:<22} {vram:.0f} GB   ${price:.4f}    {vol_ask}")

    print("-" * 80)
    return ofertas


def listar_volumenes():
    """Lista volúmenes existentes del usuario"""
    print("\n=== Tus volúmenes existentes ===\n")

    response = requests.get(f"{BASE_URL}/volumes/", headers=HEADERS, verify=False)

    if response.status_code != 200:
        print(f"  (error consultando: {response.status_code})")
        return []

    try:
        data = response.json()
        volumes = data if isinstance(data, list) else data.get("volumes", [])
    except:
        volumes = []

    if volumes:
        for v in volumes:
            vid = v.get('id', 'N/A')
            size = v.get('size', 0)
            status = v.get('status', 'N/A')
            geo = v.get('geolocation', 'N/A')
            print(f"  ID: {vid} | {size}GB | {status} | {geo}")
    else:
        print("  (ninguno)")

    return volumes


def crear_instancia(offer_id, vol_ask_id, volume_size=320, disk=32):
    """Crea instancia con volumen persistente montado en /workspace"""
    print(f"\n=== Creando instancia ===")
    print(f"  GPU Offer ID: {offer_id}")
    print(f"  Volume Ask ID: {vol_ask_id}")
    print(f"  Volume Size: {volume_size}GB")
    print(f"  Container Disk: {disk}GB")

    config = {
        "client_id": "me",
        "image": "vastai/base-image:@vastai-automatic-tag",
        "env": {
            "OPEN_BUTTON_PORT": "1111",
            "OPEN_BUTTON_TOKEN": "1",
            "JUPYTER_DIR": "/",
            "DATA_DIRECTORY": "/workspace/",
            "PORTAL_CONFIG": "localhost:1111:11111:/:Instance Portal|localhost:8080:18080:/:Jupyter|localhost:8080:8080:/terminals/1:Jupyter Terminal|localhost:8384:18384:/:Syncthing|localhost:6006:16006:/:Tensorboard"
        },
        "onstart": "entrypoint.sh",
        "disk": disk,
        "jupyter": True,
        "ssh": True,
        "direct": True,
        "create_volume": vol_ask_id,
        "volume_size": volume_size,
        "volume_mount": "/workspace"
    }

    response = requests.put(f"{BASE_URL}/asks/{offer_id}/", headers=HEADERS, json=config, verify=False)

    print(f"\nStatus: {response.status_code}")
    print(f"Respuesta: {response.text[:800]}")

    return response.json() if response.status_code == 200 else None


def main():
    print("=" * 60)
    print("  VAST.AI - Instancia + Volumen Persistente 320GB")
    print("=" * 60)

    # 1. Mostrar volúmenes existentes
    listar_volumenes()

    # 2. Buscar GPUs con volumen disponible
    ofertas = buscar_ofertas()

    if not ofertas:
        print("No hay GPUs disponibles con soporte de volumen")
        return

    # 3. Seleccionar GPU
    sel = input("\nSelecciona GPU (1-15) [1]: ").strip() or "1"

    if sel.isdigit() and 1 <= int(sel) <= 15:
        idx = int(sel) - 1
        oferta = ofertas[idx]
        offer_id = oferta["id"]
        vol_ask_id = oferta["avail_vol_ask_id"]
    else:
        print("Selección inválida")
        return

    # 4. Confirmar
    print(f"\n--- Resumen ---")
    print(f"GPU: {oferta.get('gpu_name')} (ID: {offer_id})")
    print(f"Precio: ${oferta.get('dph_total', 0):.4f}/hr")
    print(f"Volumen: 320GB en /workspace")
    print(f"Disk container: 32GB")

    if input("\n¿Crear? (s/n) [s]: ").strip().lower() == 'n':
        print("Cancelado")
        return

    # 5. Crear instancia
    crear_instancia(offer_id, vol_ask_id, volume_size=320, disk=32)

    print("\n" + "=" * 60)
    print("  Dashboard: https://cloud.vast.ai/instances/")
    print("=" * 60)


if __name__ == "__main__":
    main()
