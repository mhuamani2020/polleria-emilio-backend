-- ============================================================
-- SCRIPT DDL - POLLERIA BACKEND
-- Motor: PostgreSQL 16+
-- ============================================================

-- 1. ENUMs
-- ============================================================

CREATE TYPE user_role AS ENUM ('admin', 'cajero', 'mesero');
CREATE TYPE sede_status AS ENUM ('Activa', 'Inactiva');
CREATE TYPE inventory_status AS ENUM ('Óptimo', 'Precaución', 'Crítico');
CREATE TYPE order_status AS ENUM ('pendiente', 'en_preparacion', 'listo', 'entregado', 'cancelado');
CREATE TYPE kds_type AS ENUM ('Normal', 'Urgente');
CREATE TYPE kds_status AS ENUM ('nuevo', 'en_preparacion', 'listo');
CREATE TYPE notif_type AS ENUM ('info', 'warning', 'success', 'alert');

-- 2. TABLAS
-- ============================================================

-- 2.1 sedes
CREATE TABLE sedes (
    sede_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name           VARCHAR(150) NOT NULL,
    address        VARCHAR(255) NOT NULL,
    phone          VARCHAR(20) NOT NULL,
    manager        VARCHAR(150) NOT NULL,
    status         sede_status NOT NULL DEFAULT 'Activa',
    sales          DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2.2 users
CREATE TABLE users (
    user_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username       VARCHAR(50) NOT NULL,
    password_hash  VARCHAR(255) NOT NULL,
    role           user_role NOT NULL,
    sede_id        UUID NOT NULL REFERENCES sedes(sede_id) ON DELETE RESTRICT,
    is_active      BOOLEAN NOT NULL DEFAULT true,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_users_username UNIQUE (username)
);

CREATE INDEX idx_users_sede_id ON users(sede_id);
CREATE INDEX idx_users_role ON users(role);

-- 2.3 user_sessions (control de sesión única)
CREATE TABLE user_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    refresh_token   VARCHAR(255) NOT NULL,
    device_info     VARCHAR(255),
    ip_address      INET,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ NOT NULL,
    closed_at       TIMESTAMPTZ
);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_refresh_token ON user_sessions(refresh_token);

-- 2.4 categories
CREATE TABLE categories (
    category_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name           VARCHAR(100) NOT NULL,
    description    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_categories_name ON categories(name);

-- 2.5 products
CREATE TABLE products (
    product_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name           VARCHAR(150) NOT NULL,
    description    TEXT,
    price          DECIMAL(10,2) NOT NULL CHECK (price > 0),
    image_url      VARCHAR(500),
    icon           VARCHAR(50),
    category_id    UUID NOT NULL REFERENCES categories(category_id) ON DELETE RESTRICT,
    is_combo       BOOLEAN NOT NULL DEFAULT false,
    is_active      BOOLEAN NOT NULL DEFAULT true,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_is_combo ON products(is_combo);
CREATE INDEX idx_products_is_active ON products(is_active);

-- 2.6 combo_items (relación N:M de combos → productos)
CREATE TABLE combo_items (
    combo_id       UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    product_id     UUID NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    qty            INT NOT NULL CHECK (qty > 0),
    CONSTRAINT pk_combo_items PRIMARY KEY (combo_id, product_id),
    CONSTRAINT chk_combo_items_not_self CHECK (combo_id <> product_id)
);

-- 2.7 inventory
CREATE TABLE inventory (
    inventory_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id     UUID NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    sede_id        UUID NOT NULL REFERENCES sedes(sede_id) ON DELETE RESTRICT,
    current_stock  DECIMAL(10,2) NOT NULL CHECK (current_stock >= 0),
    minimum_stock  DECIMAL(10,2) NOT NULL CHECK (minimum_stock >= 0),
    unit           VARCHAR(20) NOT NULL,
    status         inventory_status NOT NULL DEFAULT 'Óptimo',
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_inventory_product_sede UNIQUE (product_id, sede_id)
);

CREATE INDEX idx_inventory_sede_id ON inventory(sede_id);
CREATE INDEX idx_inventory_status ON inventory(status);
CREATE INDEX idx_inventory_product_id ON inventory(product_id);

-- 2.8 orders
CREATE TABLE orders (
    order_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sede_id        UUID NOT NULL REFERENCES sedes(sede_id) ON DELETE RESTRICT,
    user_id        UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    order_date     TIMESTAMPTZ NOT NULL DEFAULT now(),
    status         order_status NOT NULL DEFAULT 'pendiente',
    total          DECIMAL(10,2) NOT NULL CHECK (total >= 0),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_orders_sede_id ON orders(sede_id);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_order_date ON orders(order_date);

-- 2.9 order_items
CREATE TABLE order_items (
    order_item_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id       UUID NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id     UUID NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    product_name   VARCHAR(150) NOT NULL,
    qty            INT NOT NULL CHECK (qty > 0),
    unit_price     DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
    subtotal       DECIMAL(10,2) GENERATED ALWAYS AS (qty * unit_price) STORED
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);

-- 2.10 kds_tickets (Kitchen Display System)
CREATE TABLE kds_tickets (
    ticket_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id       UUID NOT NULL UNIQUE REFERENCES orders(order_id) ON DELETE CASCADE,
    type           kds_type NOT NULL DEFAULT 'Normal',
    status         kds_status NOT NULL DEFAULT 'nuevo',
    label          VARCHAR(100) NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at   TIMESTAMPTZ
);

CREATE INDEX idx_kds_tickets_status ON kds_tickets(status);
CREATE INDEX idx_kds_tickets_type ON kds_tickets(type);

-- 2.11 mermas (desperdicios / bajas)
CREATE TABLE mermas (
    merma_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventory_id   UUID NOT NULL REFERENCES inventory(inventory_id) ON DELETE RESTRICT,
    quantity       DECIMAL(10,2) NOT NULL CHECK (quantity > 0),
    unit           VARCHAR(20) NOT NULL,
    reason         VARCHAR(255) NOT NULL,
    notes          TEXT,
    registered_by  UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_mermas_inventory_id ON mermas(inventory_id);
CREATE INDEX idx_mermas_registered_by ON mermas(registered_by);
CREATE INDEX idx_mermas_created_at ON mermas(created_at);

-- 2.12 notifications
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title          VARCHAR(200) NOT NULL,
    message        TEXT NOT NULL,
    type           notif_type NOT NULL DEFAULT 'info',
    is_read        BOOLEAN NOT NULL DEFAULT false,
    user_id        UUID REFERENCES users(user_id) ON DELETE CASCADE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- 3. TRIGGERS (updated_at automático)
-- ============================================================

CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sedes_updated_at
    BEFORE UPDATE ON sedes
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER trg_inventory_updated_at
    BEFORE UPDATE ON inventory
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER trg_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
