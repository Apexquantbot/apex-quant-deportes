# Apex Quant Deportes

Una sola app con tres secciones: **⚽ Fútbol**, **🏀 Baloncesto** y **🎾 Tenis**.

- Web / app: https://apexquantbot.github.io/apex-quant-deportes/
- Abrir directamente en una sección: `…/apex-quant-deportes/#futbol`, `#baloncesto` o `#tenis`

Esta app **no tiene bot propio**: solo junta las tres webs que ya existen.
Cada bot sigue funcionando por su lado (sus datos, su canal de Telegram y su cron):

| Sección | Repositorio | Web |
|---|---|---|
| Fútbol | Apexquantbot/bot-quant-futbol | https://apexquantbot.github.io/bot-quant-futbol/ |
| Baloncesto | Apexquantbot/apex-quant-baloncesto | https://apexquantbot.github.io/apex-quant-baloncesto/ |
| Tenis | Apexquantbot/apex_quant_tenis | https://apexquantbot.github.io/apex_quant_tenis/ |

Cualquier cambio que se haga en la web de un deporte aparece aquí solo, sin tocar nada.
Si algún día cambia la dirección de una de ellas, se actualiza en `index.html` (bloque `APPS`).
En móviles estrechos, las pestañas que no están elegidas muestran solo el icono.
