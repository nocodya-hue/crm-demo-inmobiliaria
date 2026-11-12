# CRM de prueba · inmobiliaria (simulación)

CRM ficticio para probar la automatización de una inmobiliaria con Make + Airtable + WhatsApp.

- `index.html` — fichas de las viviendas (abre `/#<código>` para ir a una).
- `api/viviendas/<código>.json` — la «API» que consulta Make: devuelve la ficha con el propietario y el comercial captador, o 404 si el código no existe.
- `api/viviendas/index.json` — todas las viviendas.
- `datos.py` — genera los JSON.

**Todos los datos son inventados** (propietarios, teléfonos y direcciones de ejemplo). Con una inmobiliaria real se usa la API de su CRM, nunca un repositorio público.
