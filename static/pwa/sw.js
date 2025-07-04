const CACHE_NAME = 'asistencia-qr-v1.0.0';
const STATIC_CACHE_NAME = 'asistencia-qr-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'asistencia-qr-dynamic-v1.0.0';

// Archivos esenciales para cachear
const STATIC_FILES = [
    '/',
    '/escaner/',
    '/panel/',
    '/static/pwa/manifest.json',
    '/static/pwa/icon-192x192.png',
    '/static/pwa/icon-512x512.png',
    'https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js'
];

// Archivos dinámicos que NO se deben cachear
const EXCLUDE_FROM_CACHE = [
    '/admin/',
    '/procesar-qr/',
    '/estadisticas/',
    '/exportar-csv/'
];

// Instalación del Service Worker
self.addEventListener('install', event => {
    console.log('🔧 Service Worker: Instalando...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE_NAME)
            .then(cache => {
                console.log('📦 Service Worker: Cacheando archivos estáticos');
                return cache.addAll(STATIC_FILES);
            })
            .catch(error => {
                console.error('❌ Error al cachear archivos estáticos:', error);
            })
    );
    
    // Forzar activación inmediata
    self.skipWaiting();
});

// Activación del Service Worker
self.addEventListener('activate', event => {
    console.log('✅ Service Worker: Activado');
    
    event.waitUntil(
        // Limpiar cachés antiguos
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== STATIC_CACHE_NAME && 
                        cacheName !== DYNAMIC_CACHE_NAME) {
                        console.log('🗑️ Eliminando caché antigua:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    
    // Tomar control de todas las pestañas
    self.clients.claim();
});

// Interceptar requests
self.addEventListener('fetch', event => {
    const request = event.request;
    const url = new URL(request.url);
    
    // Solo manejar requests GET
    if (request.method !== 'GET') {
        return;
    }
    
    // No cachear URLs excluidas
    if (EXCLUDE_FROM_CACHE.some(exclude => url.pathname.startsWith(exclude))) {
        return;
    }
    
    event.respondWith(
        caches.match(request)
            .then(response => {
                // Si está en caché, devolverlo
                if (response) {
                    console.log('📦 Desde caché:', request.url);
                    return response;
                }
                
                // Si no está en caché, hacer fetch
                return fetch(request)
                    .then(response => {
                        // Solo cachear respuestas exitosas
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clonar respuesta para el caché
                        const responseToCache = response.clone();
                        
                        // Cachear dinámicamente
                        caches.open(DYNAMIC_CACHE_NAME)
                            .then(cache => {
                                cache.put(request, responseToCache);
                                console.log('📦 Cacheado dinámicamente:', request.url);
                            });
                        
                        return response;
                    })
                    .catch(() => {
                        // Si falla la red, mostrar página offline para navegación
                        if (request.destination === 'document') {
                            return caches.match('/offline.html');
                        }
                    });
            })
    );
});

// Manejo de mensajes
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({version: CACHE_NAME});
    }
});

// Background sync para cuando se recupere la conexión
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        console.log('🔄 Background sync ejecutado');
        // Aquí puedes sincronizar datos pendientes
    }
});

// Push notifications (para futuras mejoras)
self.addEventListener('push', event => {
    if (event.data) {
        const data = event.data.json();
        
        const options = {
            body: data.body,
            icon: '/static/pwa/icon-192x192.png',
            badge: '/static/pwa/icon-96x96.png',
            vibrate: [100, 50, 100],
            data: {
                dateOfArrival: Date.now(),
                primaryKey: data.primaryKey
            },
            actions: [
                {
                    action: 'explore',
                    title: 'Ver detalles',
                    icon: '/static/pwa/icon-192x192.png'
                },
                {
                    action: 'close',
                    title: 'Cerrar',
                    icon: '/static/pwa/icon-192x192.png'
                }
            ]
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});