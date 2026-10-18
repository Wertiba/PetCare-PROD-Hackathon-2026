self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

// payload: { title, body, url }
self.addEventListener('push', (event) => {
  let payload = {};
  try {
    payload = event.data ? event.data.json() : {};
  } catch {
    payload = { body: event.data ? event.data.text() : '' };
  }

  const title = payload.title || 'petcare';
  const options = {
    body: payload.body || '',
    data: { url: payload.url || '/dashboard' },
  };

  event.waitUntil(
    self.registration.showNotification(title, options),
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = new URL(
    event.notification.data?.url || '/dashboard',
    self.location.origin,
  ).href;

  event.waitUntil(
    self.clients
      .matchAll({
        type: 'window',
        includeUncontrolled: true,
      })
      .then((clients) => {
        const existing = clients.find(
          (client) => client.url === targetUrl,
        );
        if (existing) return existing.focus();

        const sameOrigin = clients.find(
          (client) => 'navigate' in client,
        );
        if (sameOrigin)
          return sameOrigin
            .navigate(targetUrl)
            .then((client) => client?.focus());

        return self.clients.openWindow(targetUrl);
      }),
  );
});
