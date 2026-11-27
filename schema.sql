-- =============================================================================
-- DDL SCHEMA NOTIFICATION & CREDENTIAL (PostgreSQL)
-- Database yang ditunjuk oleh konfigurasi DATABASES.NOTIFICATION di microservice.yaml
-- (atau database default jika DATABASES.NOTIFICATION tidak dikonfigurasi)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 0. Table: public.notification_credential (Penyimpanan API Key / Token di Skema Public)
-- -----------------------------------------------------------------------------
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
