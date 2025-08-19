import xmlrpc.client
import requests

from dotenv import load_dotenv
import os

load_dotenv()



# =========== CONFIGURACIÓN ODOO ===========
url = os.getenv("URL")
db = os.getenv("DB")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# Auth
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

print("Conectado a Odoo con UID:", uid)

# =========== CONFIGURACIÓN 17TRACK ===========
API_KEY = os.getenv("API_KEY")
TRACK_URL = "https://api.17track.net/track/v1/register" 
RESULT_URL = "https://api.17track.net/track/v1/gettracklist" 
headers = {"17token": API_KEY, "Content-Type": "application/json"}

# =========== 1. Obtener envíos con guía ===========
pickings = models.execute_kw(
    db, uid, password,
    "stock.picking", "search_read",
    [[["carrier_tracking_ref", "!=", False]]],  # solo con guía
    {"fields": ["id", "name", "origin", "carrier_tracking_ref"]}
)

print(f"Se encontraron {len(pickings)} envíos con número de guía")

# =========== 2. Consultar cada guía en 17TRACK ===========
for picking in pickings:
    guia = picking["carrier_tracking_ref"]
    picking_id = picking["id"]

    print(f"\n📦 Albarán: {picking['name']} | Origen: {picking['origin']} | Guía: {guia}")

    try:
        # Paso 1: Registrar la guía en 17track
        requests.post(TRACK_URL, headers=headers, json={"number": guia})

        # Paso 2: Consultar estado
        resp = requests.post(RESULT_URL, headers=headers, json={"numbers": [guia]})
        data = resp.json()

        # Extraer status (depende de la respuesta real de 17track)
        if "data" in data and "accepted" in data["data"]:
            info = data["data"]["accepted"][0]
            status = info.get("latest_status", "Desconocido")
        else:
            status = "No encontrado"

        print(f"   ➡ Estatus recibido: {status}")

        # ==========================
        # 3. Actualizar en Odoo
        # ==========================
        models.execute_kw(
            db, uid, password,
            "stock.picking", "write",
            [[picking_id], {"x_tracking_status": status}]
        )

        print("   ✅ Estatus actualizado en Odoo")

    except Exception as e:
        print("   ❌ Error con la guía:", guia, e)
