#!/usr/bin/env python3
"""
Script para crear instancia en vast.ai con PyTorch
"""

import requests
import json
import urllib3

# Desactivar warnings de SSL (necesario por el proxy)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = "431745a46212b69187d8bdab52d5d7f368ad84c74693de168e7dc0a15d18d68f"
BASE_URL = "https://console.vast.ai/api/v0"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def buscar_ofertas(min_disk=320):
    """Busca GPUs disponibles con almacenamiento mínimo especificado"""
    print(f"\n=== Buscando GPUs con >= {min_disk}GB de almacenamiento ===\n")

    url = f"{BASE_URL}/bundles/"
    response = requests.get(url, headers=HEADERS, verify=False)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text[:500])
        return []

    data = response.json()
    todas = data.get("offers", [])

    # Filtrar: disk_space >= min_disk, rentable, ordenar por precio
    ofertas = [o for o in todas if o.get("disk_space", 0) >= min_disk and o.get("rentable", False)]
    ofertas.sort(key=lambda x: x.get("dph_total", 999))

    print(f"Encontradas {len(ofertas)} ofertas\n")
    print("Top 10 ofertas más baratas:")
    print("-" * 85)
    print(f"{'#':<3} {'ID':<10} {'GPU':<22} {'VRAM':<10} {'Disk':<12} {'$/hr':<10}")
    print("-" * 85)

    for i, o in enumerate(ofertas[:10], 1):
        gpu_name = o.get('gpu_name', 'N/A')[:21]
        vram = o.get('gpu_ram', 0) / 1024
        disk = o.get('disk_space', 0)
        price = o.get('dph_total', 0)
        offer_id = o.get('id', 'N/A')
        print(f"{i:<3} {offer_id:<10} {gpu_name:<22} {vram:.0f} GB{'':<5} {disk:.0f} GB{'':<5} ${price:.4f}")

    print("-" * 85)
    return ofertas


def crear_instancia(offer_id, disk=30):
    """Crea una instancia con la configuración especificada"""
    print(f"\n=== Creando instancia con OFFER_ID: {offer_id} ===\n")

    config = {
        "client_id": "me",
        "image": "vastai/pytorch:@vastai-automatic-tag",
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
        "direct": True
    }

    url = f"{BASE_URL}/asks/{offer_id}/"
    response = requests.put(url, headers=HEADERS, json=config, verify=False)

    print(f"Status: {response.status_code}")
    print(f"Respuesta: {response.text}")

    return response.json() if response.status_code == 200 else None


def main():
    print("=" * 50)
    print("  VAST.AI - Creador de Instancias PyTorch")
    print("=" * 50)

    # Buscar ofertas
    ofertas = buscar_ofertas(min_disk=320)

    if not ofertas:
        print("No se encontraron ofertas disponibles")
        return

    # Seleccionar oferta
    print("\n¿Qué oferta quieres usar?")
    seleccion = input("Ingresa el número (1-10) o el ID directamente [1]: ").strip()

    if not seleccion:
        seleccion = "1"

    if seleccion.isdigit() and 1 <= int(seleccion) <= 10:
        offer_id = ofertas[int(seleccion) - 1]["id"]
    else:
        offer_id = seleccion

    print(f"\nSeleccionado: {offer_id}")

    # Confirmar
    confirmar = input("\n¿Crear instancia? (s/n) [s]: ").strip().lower()
    if confirmar and confirmar != 's':
        print("Cancelado")
        return

    # Crear instancia
    resultado = crear_instancia(offer_id)

    if resultado:
        print("\n" + "=" * 50)
        print("  ¡Instancia creada!")
        print("  Dashboard: https://cloud.vast.ai/instances/")
        print("=" * 50)


if __name__ == "__main__":
    main()
