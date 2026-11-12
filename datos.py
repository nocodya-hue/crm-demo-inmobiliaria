"""CRM de prueba de la inmobiliaria: genera la «API» estática que consulta Make.
   python3 datos.py → api/viviendas/<CODIGO>.json (una ficha por vivienda) + api/viviendas/index.json
   GET <BASE>/api/viviendas/LST-2026-000101.json → 200 con la ficha; un código que no existe → 404.
   Datos FICTICIOS para la simulación (propietarios y teléfonos inventados). Los captadores son los comerciales reales del Airtable."""
import json, os

BASE = 'https://nocodya-hue.github.io/crm-demo-inmobiliaria'
HERMES = {'nombre': 'Hermes Muatetema', 'telefono': '+34624931947'}
JOSE = {'nombre': 'José Onami', 'telefono': '+34671259026'}

V = [
    # codigo, tipo, zona, direccion, ciudad, hab, baños, m2, precio, captador, propietario, teléfono propietario, descripción
    ('LST-2026-000101', 'piso', 'Ruzafa', 'C/ de Cuba 24, 3.º', 'València', 3, 2, 95, 245000, HERMES, 'Carmen Ortega Llopis', '+34600000101',
     'Piso exterior reformado, cocina abierta y balcón a la calle.'),
    ('LST-2026-000102', 'ático', 'Benimaclet', 'C/ Barón de San Petrillo 9, ático', 'València', 2, 1, 70, 189000, JOSE, 'Vicente Martí Roig', '+34600000102',
     'Ático con terraza de 20 m², muy luminoso y con ascensor.'),
    ('LST-2026-000103', 'piso', 'Campanar', 'Av. de Pío XII 40, 6.º', 'València', 4, 2, 128, 335000, HERMES, 'Lucía Ferrer Navarro', '+34600000103',
     'Piso familiar con garaje y trastero, junto al parque de Cabecera.'),
    ('LST-2026-000104', 'casa', 'Alboraia', 'C/ del Mar 15', 'Alboraia', 4, 3, 180, 410000, JOSE, 'Josep Sanchis Bou', '+34600000104',
     'Casa de dos plantas con patio, a 10 minutos de la playa de la Patacona.'),
    ('LST-2026-000105', 'estudio', 'El Carmen', 'C/ de Quart 31, 2.º', 'València', 1, 1, 42, 129000, HERMES, 'Ana Beltrán Gil', '+34600000105',
     'Estudio reformado en el centro histórico, ideal para inversión.'),
    # la vivienda de ejemplo que ya está en Airtable (Tenerife)
    ('LST-2025-000431', 'piso', 'La Salle', 'Calle Pérez Díaz 12', 'Santa Cruz de Tenerife', 3, 2, 87.5, 185000, JOSE, 'Rafael Pérez Díaz', '+34600000431',
     'Piso luminoso reformado, cocina abierta y balcón.'),
]

os.makedirs('api/viviendas', exist_ok=True)
indice = []
for (cod, tipo, zona, dire, ciudad, hab, banos, m2, precio, capt, prop, tprop, desc) in V:
    f = {'codigo': cod, 'estado': 'disponible', 'operacion': 'venta', 'tipo': tipo, 'zona': zona, 'direccion': dire, 'ciudad': ciudad,
         'habitaciones': hab, 'banos': banos, 'metros': m2, 'precio': precio, 'descripcion': desc,
         'propietario': {'nombre': prop, 'telefono': tprop}, 'captador': capt, 'ficha': f'{BASE}/#{cod}'}
    json.dump(f, open(f'api/viviendas/{cod}.json', 'w'), ensure_ascii=False, indent=1)
    indice.append(f)
json.dump(indice, open('api/viviendas/index.json', 'w'), ensure_ascii=False, indent=1)
print(len(indice), 'viviendas →', ', '.join(x['codigo'] for x in indice))
