"""CRM de prueba de la inmobiliaria: genera la «API» estática que consulta Make a partir de viviendas.json.
   python3 datos.py → api/viviendas/<CODIGO>.json (una ficha por vivienda) + api/viviendas/index.json
   GET <BASE>/api/viviendas/LST-2026-000101.json → 200 con la ficha; un código que no existe → 404.
   Datos FICTICIOS para la simulación (propietarios y teléfonos inventados). El captador es Silvestre, el único comercial.
   Para dar de alta una vivienda nueva (y avisar a S4 como un CRM real): nueva_vivienda.py"""
import json, os, glob

BASE = 'https://nocodya-hue.github.io/crm-demo-inmobiliaria'
AQUI = os.path.dirname(os.path.abspath(__file__))


def ficha_publica(v):
    """Lo que devuelve la API para una vivienda (lo que lee S3)."""
    return {k: v[k] for k in ('codigo', 'estado', 'operacion', 'tipo', 'zona', 'direccion', 'ciudad', 'habitaciones', 'banos',
                              'metros', 'precio', 'extras', 'descripcion', 'propietario', 'captador')} | {'ficha': f"{BASE}/#{v['codigo']}",
            'fotos': fotos_publicas(v)}


def fotos_publicas(v):
    """Fotos de la vivienda (de ejemplo, de Unsplash): 1.jpg = 1600 px; la página usa la versión de 720 px (-m.jpg)."""
    return [{'url': f"{BASE}/{f['archivo']}", 'archivo': f['archivo'], 'pie': f['pie']} for f in v.get('fotos', [])]


def generar():
    vs = json.load(open(os.path.join(AQUI, 'viviendas.json')))
    carpeta = os.path.join(AQUI, 'api', 'viviendas')
    os.makedirs(carpeta, exist_ok=True)
    for viejo in glob.glob(os.path.join(carpeta, '*.json')):
        os.remove(viejo)
    indice = [ficha_publica(v) for v in vs]
    for f in indice:
        json.dump(f, open(os.path.join(carpeta, f"{f['codigo']}.json"), 'w'), ensure_ascii=False, indent=1)
    json.dump(indice, open(os.path.join(carpeta, 'index.json'), 'w'), ensure_ascii=False, indent=1)
    return indice


if __name__ == '__main__':
    ind = generar()
    print(len(ind), 'viviendas →', ', '.join(x['codigo'] for x in ind))
