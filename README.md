# Apex Quant Deportes

Una sola app con dos secciones: **⚽ Fútbol** y **🏀 Baloncesto**.

- Web / app: https://apexquantbot.github.io/apex-quant-deportes/
- Abrir directamente en una sección: `…/apex-quant-deportes/#futbol` o `#baloncesto`

Esta app **no tiene bot propio**: solo junta las dos webs que ya existen.
Cada bot sigue funcionando por su lado (sus datos, su canal de Telegram y su cron):

| Sección | Repositorio | Web |
|---|---|---|
| Fútbol | Apexquantbot/bot-quant-futbol | https://apexquantbot.github.io/bot-quant-futbol/ |
| Baloncesto | Apexquantbot/apex-quant-baloncesto | https://apexquantbot.github.io/apex-quant-baloncesto/ |

Cualquier cambio que se haga en la web de fútbol o en la de baloncesto aparece aquí solo, sin tocar nada.
Si algún día cambia la dirección de una de ellas, se actualiza en `index.html` (bloque `APPS`).
