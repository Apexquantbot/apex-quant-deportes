"""
Apex Quant Deportes — AVISOS AL MÓVIL (notificaciones push de Android)

Cada pocos minutos (lo lanza .github/workflows/avisos.yml):
  1) Lee el datos.json de los 5 bots (fútbol, basket, tenis, hockey y snooker).
  2) Busca alertas nuevas y alertas que acaban de terminar (acertada / fallada / anulada).
  3) Las manda como notificación a los móviles que activaron los avisos en la app.

No toca los bots: cada uno sigue igual. Si un bot no responde, se salta y se mira en la siguiente vuelta.
La primera vez que ve un deporte solo apunta lo que ya hay (no manda avalancha de avisos antiguos).

Los móviles se guardan en el secreto APEX_PUSH (Settings → Secrets and variables → Actions).
Cada línea es un código «APEX1.…» que da la propia app (botón 🔔 → Activar avisos → Copiar código).
"""
import os
import json
import time
import base64
import hashlib
from datetime import datetime, timezone

import requests

VERSION = "1.0"
ORG = os.getenv("APEX_ORG", "Apexquantbot")

# Si algún día cambia el nombre de un repositorio, se cambia aquí (y en el bloque APPS de index.html)
DEPORTES = {
    "futbol": {"ico": "⚽", "nombre": "Fútbol", "repo": "bot-quant-futbol"},
    "basket": {"ico": "🏀", "nombre": "Basket", "repo": "apex-quant-baloncesto"},
    "tenis":  {"ico": "🎾", "nombre": "Tenis",  "repo": "apex_quant_tenis"},
    "hockey": {"ico": "🏒", "nombre": "Hockey", "repo": "apex-quant-hockey"},
    "snooker": {"ico": "🎱", "nombre": "Snooker", "repo": "apex-quant-snooker"},
}

ARCHIVO_ESTADO = "avisos_estado.json"
CONTACTO = os.getenv("PUSH_CONTACTO", "mailto:lapiruletacafepan@gmail.com")   # el servicio de avisos exige un email «mailto:»
MAX_SUELTOS = 3          # si hay más alertas nuevas a la vez en un deporte, van juntas en un solo aviso
TTL = 6 * 3600           # si el móvil está apagado, el aviso se guarda hasta 6 horas
MEMORIA = 600            # alertas recordadas por deporte (para no repetir avisos)


# ------------------------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------------------------
def recortar(t, n):
    t = " ".join(str(t or "").split())
    return t if len(t) <= n else t[: n - 1] + "…"


def id_de(a):
    i = a.get("id_alerta")
    if i:
        return str(i)
    base = f"{a.get('partido')}|{a.get('mercado')}|{a.get('fecha')}"
    return "h" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]


def cargar_estado():
    if os.path.exists(ARCHIVO_ESTADO):
        try:
            with open(ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
                e = json.load(f)
                e.setdefault("deportes", {})
                e.setdefault("dispositivos", [])
                return e
        except Exception as ex:
            print(f"Aviso leyendo {ARCHIVO_ESTADO}: {ex}")
    return {"version": 1, "deportes": {}, "dispositivos": []}


def guardar_estado(e):
    with open(ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False, indent=1)


def descargar(repo):
    """datos.json del bot. Primero el repositorio (más fresco); si falla, la web de GitHub Pages."""
    urls = [f"https://raw.githubusercontent.com/{ORG}/{repo}/main/datos.json",
            f"https://{ORG.lower()}.github.io/{repo}/datos.json"]
    for u in urls:
        try:
            r = requests.get(u, params={"t": int(time.time())}, timeout=25,
                             headers={"User-Agent": "ApexQuantAvisos/1.0", "Cache-Control": "no-cache"})
            if r.status_code == 200:
                return r.json()
            print(f"   {u}: HTTP {r.status_code}")
        except Exception as ex:
            print(f"   {u}: {ex}")
    return None


# ------------------------------------------------------------------------------
# Móviles (secreto APEX_PUSH)
# ------------------------------------------------------------------------------
def leer_dispositivos():
    crudo = os.getenv("APEX_PUSH", "")
    salida, vistos = [], set()
    for trozo in crudo.replace(",", " ").replace('"', " ").split():
        t = trozo.strip()
        if not t.startswith("APEX1."):
            continue
        try:
            b = t[6:]
            b += "=" * (-len(b) % 4)
            d = json.loads(base64.urlsafe_b64decode(b.encode("ascii")).decode("utf-8"))
            s = d.get("s") or {}
            if not d.get("k") or not s.get("endpoint") or not (s.get("keys") or {}).get("p256dh"):
                print("⚠️ Un código de APEX_PUSH está incompleto: vuelve a copiarlo desde la app")
                continue
            huella = json.dumps([s["endpoint"], sorted(d.get("d") or []), d.get("r", 1)])
            d["id"] = hashlib.sha1(huella.encode("utf-8")).hexdigest()[:12]
            if d["id"] in vistos:
                continue
            vistos.add(d["id"])
            salida.append(d)
        except Exception as ex:
            print(f"⚠️ Un código de APEX_PUSH no se puede leer ({ex}): vuelve a copiarlo desde la app")
    return salida


def enviar(disp, aviso):
    from pywebpush import webpush, WebPushException
    try:
        webpush(subscription_info=disp["s"], data=json.dumps(aviso, ensure_ascii=False),
                vapid_private_key=disp["k"], vapid_claims={"sub": CONTACTO},   # diccionario nuevo en cada envío
                ttl=TTL, headers={"Urgency": "high"}, timeout=20)
        return True
    except WebPushException as ex:
        st = getattr(getattr(ex, "response", None), "status_code", None)
        if st in (404, 410):
            print(f"   ⚠️ Móvil {disp['id']}: la suscripción ya no existe (HTTP {st}). "
                  f"Abre la app → 🔔 → Activar avisos y pega el código nuevo en APEX_PUSH.")
        else:
            print(f"   ⚠️ Móvil {disp['id']}: error al enviar (HTTP {st}): {str(ex)[:200]}")
    except Exception as ex:
        print(f"   ⚠️ Móvil {disp['id']}: error al enviar: {ex}")
    return False


# ------------------------------------------------------------------------------
# Textos de los avisos
# ------------------------------------------------------------------------------
def aviso_nueva(dep, a):
    c = DEPORTES[dep]
    cuota = a.get("cuota") or ""
    if cuota and a.get("cuota_minima"):
        cuota = f"cuota mínima {cuota}"
    hora = a.get("fecha_hora_display") or ""
    partes = [a.get("mercado") or "Nueva alerta"]
    if cuota:
        partes.append(str(cuota))
    if hora:
        partes.append(hora)
    return {"title": f"{c['ico']} {c['nombre']} · {recortar(a.get('partido'), 60)}",
            "body": recortar(" · ".join(partes), 220),
            "tag": f"{dep}-{id_de(a)}", "url": f"#{dep}"}


def _resultado(a):
    if a.get("push"):
        return "↩️ Anulada"
    if a.get("acertado") is True:
        return "✅ Acertada"
    if a.get("acertado") is False:
        return "❌ Fallada"
    return None


def aviso_resultado(dep, a):
    r = _resultado(a)
    if not r:
        return None
    c = DEPORTES[dep]
    cuerpo = a.get("mercado") or ""
    if a.get("marcador_final"):
        cuerpo += f" · {a['marcador_final']}"
    if a.get("acertado") is True and a.get("cuota"):
        cuerpo += f" · {a['cuota']}"
    return {"title": f"{r} · {c['ico']} {recortar(a.get('partido'), 55)}",
            "body": recortar(cuerpo, 220), "tag": f"{dep}-{id_de(a)}", "url": f"#{dep}"}


def aviso_grupo_nuevas(dep, lista):
    c = DEPORTES[dep]
    n = len(lista)
    nombres = "; ".join(recortar(a.get("partido"), 40) for a in lista[:3])
    if n > 3:
        nombres += f" y {n - 3} más"
    return {"title": f"{c['ico']} {c['nombre']}: {n} alertas nuevas", "body": recortar(nombres, 220),
            "tag": f"{dep}-nuevas-{int(time.time())}", "url": f"#{dep}"}


def aviso_grupo_resultados(dep, lista):
    c = DEPORTES[dep]
    ok = sum(1 for a in lista if not a.get("push") and a.get("acertado") is True)
    ko = sum(1 for a in lista if not a.get("push") and a.get("acertado") is False)
    nul = sum(1 for a in lista if a.get("push"))
    cuerpo = f"✅ {ok} acertadas · ❌ {ko} falladas" + (f" · ↩️ {nul} anuladas" if nul else "")
    return {"title": f"{c['ico']} {c['nombre']}: {len(lista)} resultados", "body": cuerpo,
            "tag": f"{dep}-resultados-{int(time.time())}", "url": f"#{dep}"}


# ------------------------------------------------------------------------------
# Ciclo
# ------------------------------------------------------------------------------
def main():
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"[{ahora}] Apex Quant Deportes · avisos v{VERSION}")
    estado = cargar_estado()
    disps = leer_dispositivos()
    print(f"📱 Móviles con avisos: {len(disps)}" + ("" if disps else " (secreto APEX_PUSH vacío o sin códigos)"))

    cola = []   # (deporte, tipo, aviso)
    for dep, cfg in DEPORTES.items():
        datos = descargar(cfg["repo"])
        if not isinstance(datos, dict):
            print(f"{cfg['ico']} {cfg['nombre']}: sin datos ahora mismo, se mira en la siguiente vuelta")
            continue
        alertas = [a for a in (datos.get("alertas") or []) if isinstance(a, dict)]
        st = estado["deportes"].setdefault(dep, {"vistas": [], "liquidadas": [], "iniciado": False})
        vistas, liquidadas = set(st["vistas"]), set(st["liquidadas"])
        nuevas, resueltas = [], []
        for a in alertas:
            i = id_de(a)
            terminada = bool(a.get("finalizado"))
            if i not in vistas:
                vistas.add(i)
                st["vistas"].append(i)
                if not terminada:
                    nuevas.append(a)
            if terminada and i not in liquidadas:
                liquidadas.add(i)
                st["liquidadas"].append(i)
                if _resultado(a):
                    resueltas.append(a)
        st["vistas"] = st["vistas"][-MEMORIA:]
        st["liquidadas"] = st["liquidadas"][-MEMORIA:]
        if not st.get("iniciado"):
            st["iniciado"] = True
            print(f"{cfg['ico']} {cfg['nombre']}: primera vez, {len(alertas)} alertas ya existentes apuntadas (sin avisar)")
            continue
        print(f"{cfg['ico']} {cfg['nombre']}: {len(nuevas)} nuevas · {len(resueltas)} terminadas")
        if len(nuevas) > MAX_SUELTOS:
            cola.append((dep, "nueva", aviso_grupo_nuevas(dep, nuevas)))
        else:
            cola += [(dep, "nueva", aviso_nueva(dep, a)) for a in nuevas]
        if len(resueltas) > MAX_SUELTOS:
            cola.append((dep, "resultado", aviso_grupo_resultados(dep, resueltas)))
        else:
            cola += [(dep, "resultado", aviso_resultado(dep, a)) for a in resueltas]

    enviados = 0
    # Bienvenida a cada móvil nuevo (o con los deportes cambiados): confirma que todo funciona
    conocidos = set(estado["dispositivos"])
    for d in disps:
        if d["id"] in conocidos:
            continue
        deps = [DEPORTES[x]["ico"] + " " + DEPORTES[x]["nombre"] for x in DEPORTES if x in (d.get("d") or DEPORTES)]
        cuerpo = "Recibirás las alertas de " + ", ".join(deps) + (" y sus resultados." if d.get("r", 1) else ".")
        if enviar(d, {"title": "🔔 Avisos de Apex Deportes activados", "body": cuerpo, "tag": "bienvenida", "url": "./"}):
            estado["dispositivos"].append(d["id"])
            enviados += 1
            print(f"   🔔 Bienvenida enviada al móvil {d['id']}")
    estado["dispositivos"] = estado["dispositivos"][-30:]

    for dep, tipo, aviso in cola:
        if not aviso:
            continue
        for d in disps:
            if dep not in (d.get("d") or DEPORTES):
                continue
            if tipo == "resultado" and not d.get("r", 1):
                continue
            if enviar(d, aviso):
                enviados += 1
            time.sleep(0.2)

    guardar_estado(estado)
    print(f"📨 Avisos enviados: {enviados}")


if __name__ == "__main__":
    main()
