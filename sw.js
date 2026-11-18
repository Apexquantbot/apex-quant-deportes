// Service Worker - Apex Quant Deportes v1.5
// Guarda la "carcasa" (pestañas e iconos) y recibe los AVISOS al móvil.
// Las apps de fútbol, basket, tenis y hockey se cargan siempre frescas desde sus propias webs.
const CACHE_NAME = 'apex-deportes-v1.5.0';
const SHELL = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(SHELL)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   // lo de fuera (las cuatro apps) pasa directo
  const clave = new Request(url.origin + url.pathname);
  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    try {
      const res = await fetch(req);                    // red primero
      if (res && res.ok) cache.put(clave, res.clone()).catch(() => {});
      return res;
    } catch (err) {
      const guardado = await cache.match(clave);
      return guardado || cache.match('./index.html');
    }
  })());
});

// ---------------- AVISOS (notificaciones push) ----------------
// Los manda avisos.py (GitHub Actions) con: { title, body, tag, url: '#futbol' | '#basket' | ... }
self.addEventListener('push', (event) => {
  let d = {};
  try { d = event.data ? event.data.json() : {}; }
  catch (e) { d = { body: event.data ? event.data.text() : '' }; }
  const opciones = {
    body: d.body || '',
    icon: './icon-192.png',
    data: { url: d.url || './' },
    vibrate: [120, 60, 120]
  };
  if (d.tag) { opciones.tag = d.tag; opciones.renotify = true; }
  event.waitUntil(self.registration.showNotification(d.title || 'Apex Quant Deportes', opciones));
});

// Al tocar el aviso: abre la app (o la trae delante) en la pestaña del deporte
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const destino = new URL((event.notification.data && event.notification.data.url) || './', self.registration.scope).href;
  event.waitUntil((async () => {
    const ventanas = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    for (const c of ventanas) {
      if (c.url.startsWith(self.registration.scope)) {
        try { await c.focus(); } catch (e) {}
        c.postMessage({ tipo: 'abrir', url: destino });
        return;
      }
    }
    await self.clients.openWindow(destino);
  })());
});
