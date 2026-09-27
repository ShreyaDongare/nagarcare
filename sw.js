/* NagarCare Service Worker v3 — Offline PWA */

var CACHE_NAME = 'nagarcare-v3';

var PRECACHE = [
  '/',
  '/report',
  '/map',
  '/select-language',
  '/login',
  '/register'
];

/* ── Install: pre-cache key pages ── */
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(PRECACHE).catch(function(err) {
        console.log('[SW] Pre-cache failed (non-fatal):', err);
      });
    })
  );
  self.skipWaiting();
});

/* ── Activate: delete old caches ── */
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(k) { return k !== CACHE_NAME; })
            .map(function(k) { return caches.delete(k); })
      );
    })
  );
  self.clients.claim();
});

/* ── Fetch: serve from cache when offline ── */
self.addEventListener('fetch', function(event) {
  var req = event.request;

  /* Skip non-GET and API calls — always go network for these */
  if (req.method !== 'GET') return;
  if (req.url.indexOf('/api/') !== -1) return;
  if (req.url.indexOf('/report') !== -1 && req.method === 'POST') return;

  event.respondWith(
    caches.match(req).then(function(cached) {
      if (cached) {
        /* Serve cached copy, refresh in background */
        var fetchPromise = fetch(req).then(function(networkResp) {
          if (networkResp && networkResp.ok && networkResp.type === 'basic') {
            caches.open(CACHE_NAME).then(function(c) {
              c.put(req, networkResp.clone());
            });
          }
          return networkResp;
        }).catch(function() { /* offline — already returned cached */ });
        return cached;
      }

      /* Nothing cached — try network */
      return fetch(req).then(function(resp) {
        if (!resp || !resp.ok) return resp;
        var clone = resp.clone();
        caches.open(CACHE_NAME).then(function(c) { c.put(req, clone); });
        return resp;
      }).catch(function() {
        /* Fully offline — return offline fallback for navigation */
        if (req.mode === 'navigate') {
          return caches.match('/').then(function(root) {
            if (root) return root;
            return new Response(
              '<!DOCTYPE html><html><head><title>NagarCare Offline</title>'
              + '<meta name="viewport" content="width=device-width,initial-scale=1">'
              + '<style>*{box-sizing:border-box;margin:0;padding:0;}'
              + 'body{font-family:sans-serif;background:#F0F4FF;min-height:100vh;'
              + 'display:flex;align-items:center;justify-content:center;padding:2rem;}'
              + '.box{background:white;border-radius:16px;padding:3rem;text-align:center;'
              + 'max-width:420px;box-shadow:0 4px 24px rgba(0,0,0,0.08);}'
              + 'h2{font-size:1.4rem;margin-bottom:0.5rem;}'
              + 'p{color:#8892A8;margin-bottom:1.5rem;line-height:1.6;}'
              + '.btn{background:#00C896;color:white;border:none;padding:12px 28px;'
              + 'border-radius:100px;cursor:pointer;font-size:1rem;font-weight:700;}'
              + '</style></head><body>'
              + '<div class="box">'
              + '<div style="font-size:3rem;margin-bottom:1rem;">📶</div>'
              + '<h2>You are offline</h2>'
              + '<p>Your complaints are saved locally and will sync automatically when you reconnect to the internet.</p>'
              + '<button class="btn" onclick="window.location.reload()">Try Again</button>'
              + '</div></body></html>',
              { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
            );
          });
        }
        /* For non-navigation offline requests just return nothing */
        return new Response('', { status: 503, statusText: 'Service Unavailable' });
      });
    })
  );
});

/* ── Background Sync (for offline complaint queue) ── */
self.addEventListener('sync', function(event) {
  if (event.tag === 'sync-complaints') {
    console.log('[SW] Background sync triggered for complaints');
    /* Actual sync is handled by the page-level JS via /api/offline-sync */
  }
});

/* ── Push notifications (placeholder) ── */
self.addEventListener('push', function(event) {
  var data = {};
  try { data = event.data ? event.data.json() : {}; } catch(e) {}
  var title = data.title || 'NagarCare Update';
  var body  = data.body  || 'Your complaint status has been updated.';
  event.waitUntil(
    self.registration.showNotification(title, {
      body: body,
      icon: '/static/images/icon-192.png',
      badge: '/static/images/icon-192.png'
    })
  );
});
