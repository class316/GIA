{% load static %}
const CACHE_NAME = 'gia-pwa-v1';
const STATIC_CACHE = [
  '/',
  '{% static "gia/pwa/icon.svg" %}',
  '{% static "gia/pwa/manifest.json" %}'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_CACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);

  if (request.method !== 'GET') {
    return;
  }

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => caches.match('/').then(response => response || new Response(
        '<h1>GIA sin conexion</h1><p>Revisa la red del servidor del taller.</p>',
        { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
      )))
    );
    return;
  }

  if (url.pathname.startsWith('/static/') && !url.pathname.endsWith('.glb')) {
    event.respondWith(
      caches.match(request).then(cached => cached || fetch(request).then(response => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
        return response;
      }))
    );
  }
});
