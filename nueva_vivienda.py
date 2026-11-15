"""Simula que la inmobiliaria capta una vivienda nueva en su CRM:
   1) la añade a viviendas.json con el siguiente código LST-2026-000NNN y un propietario ficticio,
   2) regenera la API y la publica en GitHub Pages (nocodya-hue/crm-demo-inmobiliaria) y espera a que responda,
   3) con --enviar, avisa a S4 (webhook de Make) con el mismo formato que mandaría un CRM real → S4 la cruza con los clientes.

   python3 nueva_vivienda.py --tipo piso --zona Ruzafa --calle "C/ de Sueca" --numero "41, 2.º" --hab 3 --banos 2 --m2 92 \
       --precio 230000 --extras "balcón,ascensor" --desc "Piso exterior reformado…" [--ciudad València] [--enviar]
   --prueba : no guarda, no publica ni envía; solo enseña la ficha y lo que se mandaría a S4."""
import argparse, json, os, re, subprocess, sys, tempfile, time, urllib.request, urllib.error
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos import AQUI, BASE, ficha_publica, fotos_publicas, generar

WEBHOOK_S4 = 'https://hook.eu2.make.com/steqhi98c35j345t1sdbcabi99yb2a9c'   # S4 «CRM nueva vivienda»
# El webhook de S4 está en «JSON pass-through»: entrega el cuerpo tal cual en {{1.value}} y S4·5 lo parsea. Por eso se manda
# la vivienda SIN envolver. (Hasta el 15-nov se mandaba {"value": "<json>"} y S4 recibía todos los campos vacíos.)
REPO = 'https://github.com/nocodya-hue/crm-demo-inmobiliaria.git'
GH = os.path.expanduser('~/.local/bin/gh')
SILVESTRE = {'nombre': 'Silvestre', 'telefono': '+34624931947'}
NOMBRES = ['Elena Puig Sala', 'Miguel Ángel Roca', 'Pilar Esteve Mas', 'Andrés Soler Vidal', 'Rosa Camps Ferrer', 'Javier Gil Moll',
           'Marta Llorens Peris', 'Toni Bataller Gómez', 'Isabel Navarro Climent', 'Raúl Pastor Ibáñez']


def siguiente_codigo(vs):
    nums = [int(m.group(1)) for v in vs if (m := re.match(r'LST-2026-(\d{6})$', v['codigo']))]
    return f"LST-2026-{(max(nums) + 1 if nums else 101):06d}"


def payload_crm(v):
    """Lo que manda un CRM real al webhook de S4 (mismo formato que el ejemplo del escenario)."""
    ahora = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    return {'listing_id': v['codigo'], 'operation': v['operacion'], 'type': v['tipo'], 'price': v['precio'], 'currency': 'EUR',
            'district': v['zona'], 'bedrooms': v['habitaciones'], 'bathrooms': v['banos'], 'area_m2': v['metros'],
            'address': {'street': v['calle'], 'number': v['numero'], 'city': v['ciudad'], 'province': 'Valencia', 'country': 'ES'},
            'features': v['extras'],
            'photos': [{'url': f['url'], 'order': n} for n, f in enumerate(fotos_publicas(v), 1)],   # S4·2 las guarda en Airtable
            'description': v['descripcion'], 'public_url': f"{BASE}/#{v['codigo']}",
            'source': 'crm_demo', 'created_at': ahora, 'updated_at': ahora}


def publicar(codigo):
    tmp = tempfile.mkdtemp(prefix='crm-demo-')
    cred = f'credential.helper=!{GH} auth git-credential'
    subprocess.run(['git', '-c', cred, 'clone', '-q', '--depth', '1', REPO, tmp], check=True)
    subprocess.run(['rsync', '-a', '--delete', '--exclude', '.git', '--exclude', 'README.md', '--exclude', '.nojekyll',
                    '--exclude', '__pycache__', '--exclude', '*.antes-*', AQUI + '/', tmp + '/'], check=True)
    subprocess.run(['git', '-C', tmp, 'add', '-A'], check=True)
    subprocess.run(['git', '-C', tmp, '-c', 'user.name=nocodya-hue', '-c', 'user.email=nocodya-hue@users.noreply.github.com',
                    'commit', '-q', '-m', f'Vivienda nueva {codigo}'], check=True)
    subprocess.run(['git', '-C', tmp, '-c', cred, 'push', '-q'], check=True)
    url = f'{BASE}/api/viviendas/{codigo}.json'
    for i in range(30):                       # GitHub Pages tarda ~30–60 s
        try:
            with urllib.request.urlopen(f'{url}?t={time.time()}', timeout=10) as r:
                if r.status == 200:
                    return url, (i + 1) * 10
        except urllib.error.HTTPError:
            pass
        time.sleep(10)
    raise SystemExit(f'La ficha no aparece online tras 5 min: {url}')


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--tipo', required=True); a.add_argument('--zona', required=True)
    a.add_argument('--calle', required=True); a.add_argument('--numero', default='')
    a.add_argument('--ciudad', default='València')
    a.add_argument('--hab', type=int, required=True); a.add_argument('--banos', type=int, default=1)
    a.add_argument('--m2', type=float, required=True); a.add_argument('--precio', type=int, required=True)
    a.add_argument('--extras', default=''); a.add_argument('--desc', required=True)
    a.add_argument('--enviar', action='store_true'); a.add_argument('--prueba', action='store_true')
    o = a.parse_args()

    ruta = os.path.join(AQUI, 'viviendas.json')
    vs = json.load(open(ruta))
    cod = siguiente_codigo(vs)
    n = int(cod[-3:])
    v = {'codigo': cod, 'estado': 'disponible', 'operacion': 'venta', 'tipo': o.tipo, 'zona': o.zona,
         'calle': o.calle, 'numero': o.numero, 'direccion': f'{o.calle} {o.numero}'.strip(), 'ciudad': o.ciudad,
         'habitaciones': o.hab, 'banos': o.banos, 'metros': o.m2 if o.m2 % 1 else int(o.m2), 'precio': o.precio,
         'extras': [x.strip() for x in o.extras.split(',') if x.strip()], 'descripcion': o.desc,
         'propietario': {'nombre': NOMBRES[n % len(NOMBRES)], 'telefono': f'+346000{n:05d}'}, 'captador': SILVESTRE}
    p = payload_crm(v)
    if o.prueba:
        print('FICHA (API):', json.dumps(ficha_publica(v), ensure_ascii=False, indent=1))
        print('A S4:', json.dumps(p, ensure_ascii=False)[:600], '…')
        return
    vs.append(v); json.dump(vs, open(ruta, 'w'), ensure_ascii=False, indent=1)
    generar()
    url, seg = publicar(cod)
    print(f'{cod} online en ~{seg} s → {url}')
    if o.enviar:
        req = urllib.request.Request(WEBHOOK_S4, data=json.dumps(p, ensure_ascii=False).encode(),
                                     headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=20) as r:
            print('Enviada a S4:', r.status, r.read().decode()[:100])
    else:
        print('No enviada a S4 (falta --enviar).')


if __name__ == '__main__':
    main()
