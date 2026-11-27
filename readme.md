# Notification Module (`notification`)

Modul push notification untuk `microservice` yang mendukung **OneSignal** (Mobile Android/iOS & Web Push) dan **ntfy** (HTTP pub-sub topic), dengan struktur *engine* terpisah di `notification/engine/onesignal/` dan `notification/engine/ntfy/`.

---

## 1. Setup Database

Jalankan DDL pada [schema.sql](schema.sql) di PostgreSQL (menggunakan database `DATABASES.NOTIFICATION` jika dikonfigurasi, atau database `default`):

Tambahkan `notification` di `microservice.yaml`.

```bash
DATABASES.NOTIFICATION:
    ENGINE: django.db.backends.postgresql
    HOST: localhost
    NAME: {nama-database-telegram}
    USER: postgres
    PASSWORD: {password-database-telegram}
    PORT: 5432
    MIGRATE: false
    ATOMIC_REQUESTS: false
    CONN_HEALTH_CHECKS: true
    VERSION_CHECK: false
```

Pastikan `notification` terdaftar pada `INSTALLED_MODULE` di `microservice.yaml`.

---

## 2. Registrasi Provider & Credential

### A. OneSignal (Mobile Android/iOS & Web Push)
1. Buat Provider (`POST /notification/api/provider/`):
```json
{
  "provider_name": "Main App OneSignal",
  "provider_type": "onesignal",
  "app_id": "YOUR_ONESIGNAL_APP_ID"
}
```
2. Simpan REST API Key pada Credential (`POST /notification/api/credential/`):
```json
{
  "provider_id": "<provider_id_dari_step_1>",
  "api_key": "YOUR_ONESIGNAL_REST_API_KEY"
}
```

### B. ntfy (HTTP Topic Pub-Sub)
1. Buat Provider (`POST /notification/api/provider/`):
```json
{
  "provider_name": "Ops Alert ntfy",
  "provider_type": "ntfy",
  "base_url": "https://ntfy.sh"
}
```
2. *(Opsional)* Jika server ntfy menggunakan autentikasi token, simpan di `/notification/api/credential/`.

---

## 3. Cara Subscribe di Client (Android Flutter & Web)

Agar saat user **ganti device (HP baru)** atau membuka aplikasi di **Web** tetap menerima notifikasi untuk identitas yang sama, gunakan pola `{nama_aplikasi}_{user_id}` sebagai **External ID** di OneSignal:

- **Mobile (Android/iOS):**
  ```dart
  OneSignal.login("namaapp_123");
  ```
- **Web (JS SDK):**
  ```js
  OneSignal.login("namaapp_123");
  ```

---

## 4. Mengirim Notifikasi (`POST /notification/api/outbox/`)

### Kirim ke External ID (OneSignal — Mobile + Web sekaligus)
```json
{
  "provider_id": "<onesignal_provider_id>",
  "target_type": "external_id",
  "outbox_for": "namaapp_123",
  "title": "Pesanan Diproses",
  "message": "Pesanan #INV-001 sedang dikirim.",
  "url": "https://app.example.com/orders/INV-001"
}
```

### Kirim ke Topic (ntfy)
```json
{
  "provider_id": "<ntfy_provider_id>",
  "target_type": "topic",
  "outbox_for": "server-alerts",
  "title": "CPU Alert",
  "message": "CPU usage > 90%",
  "data": {
    "priority": "high",
    "tags": ["warning", "skull"]
  }
}
```
