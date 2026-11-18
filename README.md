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
Si algún día cambia la dirección de una de ellas, se actualiza en `index.html` (bloque `APPS`).
En el móvil en vertical, las pestañas que no están elegidas muestran solo el icono.
