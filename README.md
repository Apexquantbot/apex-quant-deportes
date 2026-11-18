# Apex Quant Deportes

Una sola app con cuatro secciones: **⚽ Fútbol**, **🏀 Basket**, **🎾 Tenis** y **🏒 Hockey**.

- Web / app: https://apexquantbot.github.io/apex-quant-deportes/
- Abrir directamente en una sección: `…/apex-quant-deportes/#futbol`, `#basket`, `#tenis` o `#hockey`

Esta app **no tiene bot propio**: solo junta las cuatro webs que ya existen.
Cada bot sigue funcionando por su lado (sus datos, su canal de Telegram y su cron):

| Sección | Repositorio | Web |
|---|---|---|
| Fútbol | Apexquantbot/bot-quant-futbol | https://apexquantbot.github.io/bot-quant-futbol/ |
| Basket | Apexquantbot/apex-quant-baloncesto | https://apexquantbot.github.io/apex-quant-baloncesto/ |
| Tenis | Apexquantbot/apex_quant_tenis | https://apexquantbot.github.io/apex_quant_tenis/ |
| Hockey | Apexquantbot/apex-quant-hockey | https://apexquantbot.github.io/apex-quant-hockey/ |

Cualquier cambio que se haga en la web de un deporte aparece aquí solo, sin tocar nada.
Si algún día cambia la dirección de una de ellas, se actualiza en `index.html` (bloque `APPS`) **y** en `avisos.py` (bloque `DEPORTES`).
En el móvil en vertical, las pestañas que no están elegidas muestran solo el icono.

---

## 🔔 Avisos al móvil (v1.5)

La app manda una **notificación de Android** cuando cualquiera de los 4 bots da una **alerta nueva**
y, si quieres, cuando **termina** (✅ acertada, ❌ fallada o ↩️ anulada). Llega aunque la app esté cerrada.
Al tocarla se abre la app directamente en la pestaña de ese deporte.

### Cómo funciona
- `avisos.py` lo lanza GitHub Actions (`.github/workflows/avisos.yml`) cada 5 minutos desde cron-job.org.
- Lee el `datos.json` de los 4 bots y compara con lo que ya avisó. **No toca los bots.**
- Si en un deporte salen más de 3 alertas a la vez (p. ej. la previa del hockey), van juntas en un solo aviso.
- Lo ya avisado se guarda en la rama **`avisos-estado`** (aparte, para no reconstruir la web cada vez).
- La primera vez solo apunta las alertas que ya había: no manda avisos antiguos.
- Todo gratis: el servicio de avisos de Chrome (Google) es gratuito y GitHub Actions es gratis en repos públicos.

### Puesta en marcha (una sola vez)

**1. Permiso para guardar lo avisado**
1. En Chrome, entra en `github.com/Apexquantbot/apex-quant-deportes`.
2. Toca **Settings** (si no lo ves, pon el móvil en «Sitio de ordenador» desde el menú ⋮ de Chrome).
3. En el menú de la izquierda: **Actions → General**.
4. Baja hasta **Workflow permissions**, marca **Read and write permissions** y toca **Save**.

**2. Activar los avisos en el móvil**
1. Abre la app **Apex Deportes** (la instalada, no una pestaña normal de Chrome).
2. Toca la campana **🔔** de arriba (al lado de ↻).
3. Marca los deportes que quieres (vienen los 4) y si quieres también los resultados.
4. Toca **Activar avisos** → cuando el móvil pregunte, toca **Permitir**.
5. Aparece un código largo que empieza por `APEX1.` → toca **📋 Copiar código**.
6. (Opcional) Toca **Probar aviso**: debe salir una notificación de prueba.

**3. Guardar el código en GitHub**
1. Vuelve a `github.com/Apexquantbot/apex-quant-deportes` → **Settings**.
2. Menú izquierdo: **Secrets and variables → Actions**.
3. Toca **New repository secret**.
4. **Name:** `APEX_PUSH` (exactamente así, en mayúsculas).
5. **Secret:** mantén pulsado y **Pegar** el código.
6. Toca **Add secret**.

**4. Primera prueba**
1. En el repo, pestaña **Actions** → a la izquierda **Avisos al móvil**.
2. Toca **Run workflow** → **Run workflow** (rama `main`).
3. En 1-2 minutos te llega **«🔔 Avisos de Apex Deportes activados»**. ¡Listo!

**5. Que mire cada 5 minutos (cron-job.org)**
1. Añade este repo al token que ya usas en cron-job.org: en `github.com/settings/personal-access-tokens` → toca el token →
   **Edit** → en **Repository access** añade **apex-quant-deportes** → comprueba que **Actions** está en **Read and write** → **Update**.
2. En cron-job.org → **Create cronjob**:
   - **Title:** `Apex Quant Avisos`
   - **URL:** `https://api.github.com/repos/Apexquantbot/apex-quant-deportes/actions/workflows/avisos.yml/dispatches`
   - **Execution schedule:** cada **5 minutos**
   - Pestaña **Advanced**: método **POST**; cabeceras `Authorization: Bearer <tu token>` y `Accept: application/vnd.github+json`; cuerpo `{"ref":"main"}`
   - **Create** y luego **Test run**: debe responder **204**.
   (Si cron-job.org falla, GitHub lo lanza igualmente cada ~10-30 minutos como respaldo.)

**6. Xiaomi / Redmi: que no corte los avisos**
1. Ajustes → **Aplicaciones** → **Administrar aplicaciones** → **Chrome** → **Ahorro de batería** → **Sin restricciones**.
2. En la misma pantalla de Chrome: **Inicio automático** activado y **Notificaciones** permitidas.
3. Haz lo mismo con **Apex Deportes** si aparece como app aparte en la lista.

### Cambiar deportes, otro móvil o desactivar
- **Cambiar qué deportes recibes:** 🔔 → marca/desmarca → copia el código nuevo → GitHub → Secrets → `APEX_PUSH` → **✏️ (Update)** → pega → **Update secret**.
- **Otro móvil o tablet:** actívalo allí también y en `APEX_PUSH` pon **los dos códigos, uno en cada línea**.
- **Desactivar:** 🔔 → **Desactivar avisos en este móvil** (pulsar dos veces) y, si quieres, borra el secreto.
- **Si dejan de llegar** (p. ej. tras borrar datos de Chrome o reinstalar la app): 🔔 → Activar avisos → copia el código nuevo y cámbialo en `APEX_PUSH`.
  En **Actions → Avisos al móvil** el registro dice «la suscripción ya no existe» cuando pasa esto.

Archivos: `index.html`, `manifest.json`, `sw.js`, `avisos.py`, `.github/workflows/avisos.yml`, `README.md`, iconos «APEX DEPORTES».
