import xmlrpc.client

url = "https://deviart-sandbox-22967801.dev.odoo.com"
db = "deviart-sandbox-22967801"   # nombre de tu base de datos
username = "alex@emakers.mx"   # tu usuario admin
password = "Uupz_2024*-"

# auth
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

print("UID conectado:", uid)

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Prueba orders
"""orders = models.execute_kw(
    db, uid, password,
    "sale.order", "search_read",
    [[]], {"fields": ["name", "partner_id", "amount_total"], "limit": 5}
)


for order in orders:
    print(f"Pedido: {order['name']} | Cliente: {order['partner_id'][1]} | Total: {order['amount_total']}")"""
    
# Para rastreos
pickings = models.execute_kw(
    db, uid, password,
    "stock.picking", "search_read",
    [[]], 
    {"fields": ["name", "origin", "carrier_tracking_ref", "state"], "limit": 5}
)

for picking in pickings:
    print(f"Albarán: {picking['name']} | Origen: {picking['origin']} | "
          f"Guía: {picking['carrier_tracking_ref']} | Estado: {picking['state']}")
