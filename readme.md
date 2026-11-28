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
    NAME: {nama-database-notification}
    USER: postgres
    PASSWORD: {password-database-notification}
    PORT: 5432
    MIGRATE: false
    ATOMIC_REQUESTS: false
    CONN_HEALTH_CHECKS: true
    VERSION_CHECK: false
```

Pastikan `notification` terdaftar pada `INSTALLED_MODULE` di `microservice.yaml`.

---

## 2. Cara Menjalankan Layanan

Jalankan **layanan berikut pada terminal terpisah**:
```bash
python manage.py runhuey --queue notification
```

---

## 3. Registrasi Provider & Credential

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

### B. ntfy (Self-Hosted Portable + FCM Wakeup)
1. **Aktifkan FCM Wakeup *(agar notif masuk saat app Android di-kill)*:**
   - Unduh **Firebase Service Account JSON** dari Firebase Console (*Project Settings → Service accounts → Generate new private key*).
   - Letakkan file `.json` tersebut di `notification/engine/ntfy/` *(otomatis diabaikan `.gitignore`)*, lalu arahkan `firebase-key-file` di [server.yml](engine/ntfy/server.yml) ke path file tersebut.
   - Pastikan aplikasi Android (`ntfy_app`) memakai `android/app/google-services.json` dari project Firebase yang **sama**.
2. **Jalankan Service:**
   ```powershell
   python manage.py runntfy
   ```
   *(Jika key FCM terbaca, terminal `runntfy` akan menampilkan `FCM wakeup aktif` dan server berjalan di `http://127.0.0.1:8085` tanpa login).*
3. **Daftarkan Provider (`POST /notification/api/provider/`):**
```json
{
  "provider_name": "Ops Alert ntfy",
  "provider_type": "ntfy",
  "base_url": "http://127.0.0.1:8085"
}
```
*(Ganti `base_url` menjadi `https://ntfy.sh` jika memakai server publik. Endpoint `/notification/api/credential/` hanya perlu diisi jika server ntfy menggunakan Bearer token).*

---

## 4. Cara Subscribe di Client (Android Flutter & Web)

Agar saat user **ganti device (HP baru)** atau membuka aplikasi di **Web** tetap menerima notifikasi untuk identitas yang sama, gunakan pola `{nama_aplikasi}_{user_id}` (misal `namaapp_123`):

### A. OneSignal (`External ID`)
- **Mobile (Android/iOS):**
  ```dart
  OneSignal.login("namaapp_123");
  ```
- **Web (JS SDK):**
  ```js
  OneSignal.login("namaapp_123");
  ```

### B. ntfy (`Topic`)
Gunakan `{nama_aplikasi}_{user_id}` langsung sebagai nama **topic**:
- **Android (Flutter — Background/Killed via FCM + Foreground via HTTP Stream):**
  ```dart
  // 1. Wajib agar tetap masuk saat app di-kill (butuh firebase-key-file di server ntfy)
  await FirebaseMessaging.instance.subscribeToTopic("namaapp_123");

  // 2. Stream realtime saat app dibuka: GET http://<server-ntfy>/namaapp_123/json
  ```
- **Web (JS SSE / EventSource):**
  ```js
  const es = new EventSource("http://127.0.0.1:8085/namaapp_123/sse");
  es.onmessage = (e) => console.log(JSON.parse(e.data));
  ```

---

## 5. Mengirim Notifikasi (`POST /notification/api/outbox/`)

### A. OneSignal

#### 1. Kirim Dasar ke External ID (Mobile + Web sekaligus)
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

#### 2. Kirim dengan Gambar & Tombol
```json
{
  "provider_id": "<onesignal_provider_id>",
  "target_type": "external_id",
  "outbox_for": "namaapp_123",
  "title": "Promo Spesial",
  "message": "Cek penawaran hari ini!",
  "url": "https://app.example.com/promo",
  "data": {
    "big_picture": "https://picsum.photos/800/400",
    "large_icon": "https://picsum.photos/200",
    "buttons": [
      {"id": "btn_open", "text": "Buka"},
      {"id": "btn_close", "text": "Tutup"}
    ],
    "web_buttons": [
      {"id": "btn_web", "text": "Lihat Detail", "url": "https://app.example.com/promo"}
    ]
  }
}
```
- `big_picture`: gambar besar pada notifikasi Android.
- `large_icon`: ikon besar di sebelah teks notifikasi.
- `buttons`: tombol aksi untuk Mobile (Android/iOS).
- `web_buttons`: tombol aksi untuk Web.

---

### B. ntfy

#### 1. Kirim Dasar ke Topic
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

#### 2. Kirim dengan Gambar & Tombol Aksi
```json
{
  "provider_id": "<ntfy_provider_id>",
  "target_type": "topic",
  "outbox_for": "server-alerts",
  "title": "Server Alert",
  "message": "Disk hampir penuh!",
  "data": {
    "attach": "https://picsum.photos/800/400",
    "filename": "disk.jpg",
    "actions": "view, Buka Dashboard, https://app.example.com; http, Restart, https://app.example.com/restart, method=POST"
  }
}
```
- `attach`: URL gambar/lampiran yang akan ditampilkan di notifikasi ntfy.
- `filename` *(opsional)*: nama file lampiran.
- `actions` *(opsional)*: tombol aksi ntfy.

---

## 5. Database DDL (Schema Notification)

Berikut adalah query DDL PostgreSQL lengkap untuk skema dan tabel-tabel modul `notification` (sama dengan [schema.sql](schema.sql)):

```sql
CREATE TABLE IF NOT EXISTS "public"."notification_credential" (
    "created" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "modified" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "is_removed" BOOLEAN NOT NULL DEFAULT FALSE,
    "read_only" BOOLEAN NOT NULL DEFAULT FALSE,
    "enable" BOOLEAN NOT NULL DEFAULT TRUE,
    "properties" JSONB NOT NULL DEFAULT '{}'::jsonb,
    "description" TEXT NULL,
    "credential_id" VARCHAR(25) NOT NULL,
    "provider_id" VARCHAR(25) NOT NULL,
    "api_key" VARCHAR(512) NOT NULL,
    "status" VARCHAR(100) NOT NULL DEFAULT 'ACTIVE',
    CONSTRAINT "notification_credential_pkey" PRIMARY KEY ("credential_id"),
    CONSTRAINT "notification_credential_provider_id_uniq" UNIQUE ("provider_id")
);

CREATE SCHEMA IF NOT EXISTS "notification";

-- -----------------------------------------------------------------------------
-- 1. Table: notification.provider
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "notification"."provider" (
    "created" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "modified" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "is_removed" BOOLEAN NOT NULL DEFAULT FALSE,
    "read_only" BOOLEAN NOT NULL DEFAULT FALSE,
    "enable" BOOLEAN NOT NULL DEFAULT TRUE,
    "properties" JSONB NOT NULL DEFAULT '{}'::jsonb,
    "description" TEXT NULL,
    "provider_id" VARCHAR(25) NOT NULL,
    "provider_name" VARCHAR(255) NOT NULL,
    "provider_type" VARCHAR(50) NOT NULL DEFAULT 'onesignal',
    "app_id" VARCHAR(255) NULL,
    "base_url" VARCHAR(255) NULL,
    "data" JSONB NOT NULL DEFAULT '{}'::jsonb,
    "status" VARCHAR(100) NOT NULL DEFAULT 'ACTIVE',
    CONSTRAINT "notification_provider_pkey" PRIMARY KEY ("provider_id")
);

-- -----------------------------------------------------------------------------
-- 2. Table: notification.template
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "notification"."template" (
    "created" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "modified" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "is_removed" BOOLEAN NOT NULL DEFAULT FALSE,
    "read_only" BOOLEAN NOT NULL DEFAULT FALSE,
    "enable" BOOLEAN NOT NULL DEFAULT TRUE,
    "properties" JSONB NOT NULL DEFAULT '{}'::jsonb,
    "description" TEXT NULL,
    "template_id" VARCHAR(100) NOT NULL,
    "template_name" VARCHAR(255) NOT NULL,
    "title_template" TEXT NULL,
    "template" TEXT NOT NULL,
    "status" VARCHAR(100) NOT NULL DEFAULT 'ACTIVE',
    "provider_id" VARCHAR(25) NULL,
    CONSTRAINT "notification_template_pkey" PRIMARY KEY ("template_id"),
    CONSTRAINT "notification_template_template_provider_id_uniq" UNIQUE ("template", "provider_id"),
    CONSTRAINT "notification_template_provider_id_fk"
        FOREIGN KEY ("provider_id") REFERENCES "notification"."provider"("provider_id") DEFERRABLE INITIALLY DEFERRED
);

-- -----------------------------------------------------------------------------
-- 3. Table: notification.outbox
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "notification"."outbox" (
    "created" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "modified" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "is_removed" BOOLEAN NOT NULL DEFAULT FALSE,
    "read_only" BOOLEAN NOT NULL DEFAULT FALSE,
    "enable" BOOLEAN NOT NULL DEFAULT TRUE,
    "properties" JSONB NOT NULL DEFAULT '{}'::jsonb,
    "description" TEXT NULL,
    "outbox_id" VARCHAR(100) NOT NULL,
    "sent_id" VARCHAR(100) NOT NULL,
    "title" VARCHAR(255) NULL,
    "message" TEXT NULL,
    "target_type" VARCHAR(50) NOT NULL DEFAULT 'external_id',
    "outbox_for" VARCHAR(255) NOT NULL,
    "url" TEXT NULL,
    "prepare_date" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "retry" INTEGER NOT NULL DEFAULT 0,
    "scheduled" BOOLEAN NOT NULL DEFAULT FALSE,
    "scheduled_date" TIMESTAMPTZ NULL,
    "data" JSONB NOT NULL DEFAULT '{}'::jsonb,
    "status" VARCHAR(100) NOT NULL DEFAULT 'QUEUED',
    "provider_id" VARCHAR(25) NULL,
    "template_id" VARCHAR(100) NULL,
    CONSTRAINT "notification_outbox_pkey" PRIMARY KEY ("outbox_id"),
    CONSTRAINT "notification_outbox_provider_id_fk"
        FOREIGN KEY ("provider_id") REFERENCES "notification"."provider"("provider_id") DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "notification_outbox_template_id_fk"
        FOREIGN KEY ("template_id") REFERENCES "notification"."template"("template_id") DEFERRABLE INITIALLY DEFERRED
);

-- -----------------------------------------------------------------------------
-- 4. Table: notification.sent
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "notification"."sent" (
    "created" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "modified" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "is_removed" BOOLEAN NOT NULL DEFAULT FALSE,
    "read_only" BOOLEAN NOT NULL DEFAULT FALSE,
    "enable" BOOLEAN NOT NULL DEFAULT TRUE,
    "properties" JSONB NOT NULL DEFAULT '{}'::jsonb,
    "description" TEXT NULL,
    "sent_id" VARCHAR(100) NOT NULL,
    "title" VARCHAR(255) NULL,
    "message" TEXT NULL,
    "target_type" VARCHAR(50) NOT NULL DEFAULT 'external_id',
    "sent_for" VARCHAR(255) NOT NULL,
    "url" TEXT NULL,
    "sent_date" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "prepare_date" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "retry" INTEGER NOT NULL DEFAULT 0,
    "scheduled" BOOLEAN NOT NULL DEFAULT FALSE,
    "scheduled_date" TIMESTAMPTZ NULL,
    "data" JSONB NOT NULL DEFAULT '{}'::jsonb,
    "status" VARCHAR(100) NOT NULL DEFAULT 'SENT',
    "provider_id" VARCHAR(25) NULL,
    "template_id" VARCHAR(100) NULL,
    CONSTRAINT "notification_sent_pkey" PRIMARY KEY ("sent_id"),
    CONSTRAINT "notification_sent_provider_id_fk"
        FOREIGN KEY ("provider_id") REFERENCES "notification"."provider"("provider_id") DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "notification_sent_template_id_fk"
        FOREIGN KEY ("template_id") REFERENCES "notification"."template"("template_id") DEFERRABLE INITIALLY DEFERRED
);

-- -----------------------------------------------------------------------------
-- Indexes
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS "notification_outbox_provider_id_idx" ON "notification"."outbox" ("provider_id");
CREATE INDEX IF NOT EXISTS "notification_outbox_template_id_idx" ON "notification"."outbox" ("template_id");
CREATE INDEX IF NOT EXISTS "notification_sent_provider_id_idx" ON "notification"."sent" ("provider_id");
CREATE INDEX IF NOT EXISTS "notification_sent_template_id_idx" ON "notification"."sent" ("template_id");
CREATE INDEX IF NOT EXISTS "notification_template_provider_id_idx" ON "notification"."template" ("provider_id");
```

---

## 6. Dummy Data (PostgreSQL)

Contoh data awal untuk pengujian langsung di database:

```sql
-- 1. Provider OneSignal & ntfy
INSERT INTO "notification"."provider" ("provider_id", "provider_name", "provider_type", "app_id", "base_url", "status")
VALUES
    ('prov_onesignal_001', 'HKAGROUP OneSignal', 'onesignal', 'YOUR_ONESIGNAL_APP_ID', NULL, 'ACTIVE'),
    ('prov_ntfy_001', 'Self-Hosted ntfy', 'ntfy', NULL, 'http://127.0.0.1:8085', 'ACTIVE')
ON CONFLICT ("provider_id") DO NOTHING;

-- 2. Credential OneSignal (REST API Key)
INSERT INTO "public"."notification_credential" ("credential_id", "provider_id", "api_key", "status")
VALUES
    ('cred_onesignal_001', 'prov_onesignal_001', 'YOUR_ONESIGNAL_REST_API_KEY', 'ACTIVE')
ON CONFLICT ("credential_id") DO NOTHING;

-- 3. Template Notifikasi
INSERT INTO "notification"."template" ("template_id", "template_name", "title_template", "template", "provider_id", "status")
VALUES
    ('tpl_order_001', 'Update Pesanan', 'Pesanan {{ order_no }}', 'Halo {{ name }}, pesanan {{ order_no }} berstatus {{ state }}.', 'prov_onesignal_001', 'ACTIVE')
ON CONFLICT ("template_id") DO NOTHING;

-- 4. Contoh Outbox (OneSignal & ntfy)
INSERT INTO "notification"."outbox" ("outbox_id", "sent_id", "provider_id", "target_type", "outbox_for", "title", "message", "data", "status")
VALUES
    ('out_os_001', 'sent_os_001', 'prov_onesignal_001', 'external_id', 'namaapp_123', 'Tes OneSignal', 'Halo dari dummy data!', '{}'::jsonb, 'QUEUED'),
    ('out_ntfy_001', 'sent_ntfy_001', 'prov_ntfy_001', 'topic', 'hkagroup_alert_123', 'Tes ntfy', 'Halo dari dummy data ntfy!', '{"priority": "high", "tags": ["bell"]}'::jsonb, 'QUEUED')
ON CONFLICT ("outbox_id") DO NOTHING;
```


