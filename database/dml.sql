-- ============================================================
-- SCRIPT DML - DATOS DE PRUEBA POLLERIA
-- ============================================================

-- 1. SEDES
-- ============================================================
INSERT INTO sedes (sede_id, name, address, phone, manager, status, sales) VALUES
('a1b2c3d4-0001-4000-8000-000000000001', 'Sede Central', 'Av. La Marina 1234', '999-111-222', 'Carlos López', 'Activa', 28500.00),
('a1b2c3d4-0002-4000-8000-000000000002', 'Sede Norte', 'Jr. Los Olivos 567', '999-333-444', 'María García', 'Activa', 19300.00),
('a1b2c3d4-0003-4000-8000-000000000003', 'Sede Sur', 'Av. Benavides 890', '999-555-666', 'José Martínez', 'Inactiva', 0.00)
ON CONFLICT (sede_id) DO NOTHING;

-- 2. USUARIOS
-- ============================================================
-- password_hash para todos: "Polleria123!" (bcrypt)
INSERT INTO users (user_id, username, password_hash, role, sede_id, is_active) VALUES
('b2c3d4e5-0001-4000-8000-000000000001', 'admin.central',
 '$2b$12$LJ3m4ys3Lk0TSwHlMH4v7OqGmHOPpMj6YxFQWqR6VfRy5Kv5YiF3q',
 'admin', 'a1b2c3d4-0001-4000-8000-000000000001', true),

('b2c3d4e5-0002-4000-8000-000000000002', 'cajero.central',
 '$2b$12$LJ3m4ys3Lk0TSwHlMH4v7OqGmHOPpMj6YxFQWqR6VfRy5Kv5YiF3q',
 'cajero', 'a1b2c3d4-0001-4000-8000-000000000001', true),

('b2c3d4e5-0003-4000-8000-000000000003', 'mesero.central',
 '$2b$12$LJ3m4ys3Lk0TSwHlMH4v7OqGmHOPpMj6YxFQWqR6VfRy5Kv5YiF3q',
 'mesero', 'a1b2c3d4-0001-4000-8000-000000000001', true),

('b2c3d4e5-0004-4000-8000-000000000004', 'cajero.norte',
 '$2b$12$LJ3m4ys3Lk0TSwHlMH4v7OqGmHOPpMj6YxFQWqR6VfRy5Kv5YiF3q',
 'cajero', 'a1b2c3d4-0002-4000-8000-000000000002', true)
ON CONFLICT (username) DO NOTHING;

-- 3. CATEGORÍAS
-- ============================================================
INSERT INTO categories (category_id, name, description) VALUES
('c3d4e5f6-0001-4000-8000-000000000001', 'Parrilladas', 'Platos a la parrilla'),
('c3d4e5f6-0002-4000-8000-000000000002', 'Bebidas', 'Bebidas frías y calientes'),
('c3d4e5f6-0003-4000-8000-000000000003', 'Entradas', 'Entradas y aperitivos'),
('c3d4e5f6-0004-4000-8000-000000000004', 'Combos', 'Combos promocionales'),
('c3d4e5f6-0005-4000-8000-000000000005', 'Insumos', 'Insumos de cocina')
ON CONFLICT (category_id) DO NOTHING;

-- 4. PRODUCTOS
-- ============================================================
INSERT INTO products (product_id, name, description, price, icon, category_id, is_combo) VALUES
('d4e5f6a7-0001-4000-8000-000000000001', 'Pollo Entero Asado', 'Pollo entero asado al carbón', 45.00, 'set_meal', 'c3d4e5f6-0001-4000-8000-000000000001', false),
('d4e5f6a7-0002-4000-8000-000000000002', '1/4 Pollo Asado', 'Cuarto de pollo asado', 15.00, 'restaurant', 'c3d4e5f6-0001-4000-8000-000000000001', false),
('d4e5f6a7-0003-4000-8000-000000000003', 'Pollo a la Brasa', 'Pollo a la brasa con ensalada y papas', 55.00, 'local_fire_department', 'c3d4e5f6-0001-4000-8000-000000000001', false),
('d4e5f6a7-0004-4000-8000-000000000004', 'Anticuchos (4 und)', 'Anticuchos de corazón', 25.00, 'skillet', 'c3d4e5f6-0001-4000-8000-000000000001', false),
('d4e5f6a7-0005-4000-8000-000000000005', 'Papa Rellena', 'Papa rellena tradicional', 8.00, 'lunch_dining', 'c3d4e5f6-0003-4000-8000-000000000003', false),
('d4e5f6a7-0006-4000-8000-000000000006', 'Inka Cola 1L', 'Gaseosa Inka Cola 1 litro', 7.00, 'liquor', 'c3d4e5f6-0002-4000-8000-000000000002', false),
('d4e5f6a7-0007-4000-8000-000000000007', 'Agua Mineral 500ml', 'Agua mineral sin gas', 3.00, 'water_drop', 'c3d4e5f6-0002-4000-8000-000000000002', false),
('d4e5f6a7-0008-4000-8000-000000000008', 'Causa Rellena', 'Causa rellena de pollo', 18.00, 'tapas', 'c3d4e5f6-0003-4000-8000-000000000003', false),
('d4e5f6a7-0009-4000-8000-000000000009', 'Papa a la Huancaína', 'Papa a la huancaína clásica', 12.00, 'tapas', 'c3d4e5f6-0003-4000-8000-000000000003', false),

-- Combos
('d4e5f6a7-0010-4000-8000-000000000010', 'Combo Familiar',
 'Pollo entero + 4 papas + 1L Inka Cola', 59.00, 'diversity_1',
 'c3d4e5f6-0004-4000-8000-000000000004', true),

('d4e5f6a7-0011-4000-8000-000000000011', 'Combo Pareja',
 '1/4 Pollo x2 + 2 papas + 2 bebidas', 39.00, 'favorite',
 'c3d4e5f6-0004-4000-8000-000000000004', true)
ON CONFLICT (product_id) DO NOTHING;

-- 5. COMBO ITEMS (relación combo → productos)
-- ============================================================
INSERT INTO combo_items (combo_id, product_id, qty) VALUES
('d4e5f6a7-0010-4000-8000-000000000010', 'd4e5f6a7-0001-4000-8000-000000000001', 1),
('d4e5f6a7-0010-4000-8000-000000000010', 'd4e5f6a7-0006-4000-8000-000000000006', 1),
('d4e5f6a7-0011-4000-8000-000000000011', 'd4e5f6a7-0002-4000-8000-000000000002', 2),
('d4e5f6a7-0011-4000-8000-000000000011', 'd4e5f6a7-0006-4000-8000-000000000006', 2)
ON CONFLICT (combo_id, product_id) DO NOTHING;

-- 6. INVENTARIO
-- ============================================================
INSERT INTO inventory (inventory_id, product_id, sede_id, current_stock, minimum_stock, unit, status) VALUES
('e5f6a7b8-0001-4000-8000-000000000001', 'd4e5f6a7-0001-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001', 15, 5, 'unidades', 'Óptimo'),
('e5f6a7b8-0002-4000-8000-000000000002', 'd4e5f6a7-0002-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000001', 3, 5, 'unidades', 'Crítico'),
('e5f6a7b8-0003-4000-8000-000000000003', 'd4e5f6a7-0006-4000-8000-000000000006', 'a1b2c3d4-0001-4000-8000-000000000001', 8, 10, 'unidades', 'Precaución'),
('e5f6a7b8-0004-4000-8000-000000000004', 'd4e5f6a7-0005-4000-8000-000000000005', 'a1b2c3d4-0001-4000-8000-000000000001', 25, 10, 'unidades', 'Óptimo'),
('e5f6a7b8-0005-4000-8000-000000000005', 'd4e5f6a7-0001-4000-8000-000000000001', 'a1b2c3d4-0002-4000-8000-000000000002', 10, 5, 'unidades', 'Óptimo'),
('e5f6a7b8-0006-4000-8000-000000000006', 'd4e5f6a7-0006-4000-8000-000000000006', 'a1b2c3d4-0002-4000-8000-000000000002', 2, 5, 'unidades', 'Crítico')
ON CONFLICT (product_id, sede_id) DO NOTHING;

-- 7. PEDIDOS + ORDER ITEMS + KDS TICKETS
-- ============================================================
INSERT INTO orders (order_id, sede_id, user_id, order_date, status, total) VALUES
('f6a7b8c9-0001-4000-8000-000000000001', 'a1b2c3d4-0001-4000-8000-000000000001', 'b2c3d4e5-0002-4000-8000-000000000002',
 '2026-05-26 12:30:00-05', 'entregado', 55.00),
('f6a7b8c9-0002-4000-8000-000000000002', 'a1b2c3d4-0001-4000-8000-000000000001', 'b2c3d4e5-0002-4000-8000-000000000002',
 '2026-05-26 12:45:00-05', 'en_preparacion', 25.00),
('f6a7b8c9-0003-4000-8000-000000000003', 'a1b2c3d4-0001-4000-8000-000000000001', 'b2c3d4e5-0002-4000-8000-000000000002',
 '2026-05-26 13:00:00-05', 'pendiente', 59.00),
('f6a7b8c9-0004-4000-8000-000000000004', 'a1b2c3d4-0002-4000-8000-000000000002', 'b2c3d4e5-0004-4000-8000-000000000004',
 '2026-05-26 11:15:00-05', 'entregado', 37.00),
('f6a7b8c9-0005-4000-8000-000000000005', 'a1b2c3d4-0002-4000-8000-000000000002', 'b2c3d4e5-0004-4000-8000-000000000004',
 '2026-05-26 13:10:00-05', 'pendiente', 15.00)
ON CONFLICT (order_id) DO NOTHING;

-- order_items
INSERT INTO order_items (order_item_id, order_id, product_id, product_name, qty, unit_price) VALUES
('a7b8c9d0-0001-4000-8000-000000000001', 'f6a7b8c9-0001-4000-8000-000000000001', 'd4e5f6a7-0003-4000-8000-000000000003', 'Pollo a la Brasa', 1, 55.00),
('a7b8c9d0-0002-4000-8000-000000000002', 'f6a7b8c9-0002-4000-8000-000000000002', 'd4e5f6a7-0004-4000-8000-000000000004', 'Anticuchos (4 und)', 1, 25.00),
('a7b8c9d0-0003-4000-8000-000000000003', 'f6a7b8c9-0003-4000-8000-000000000003', 'd4e5f6a7-0010-4000-8000-000000000010', 'Combo Familiar', 1, 59.00),
('a7b8c9d0-0004-4000-8000-000000000004', 'f6a7b8c9-0004-4000-8000-000000000004', 'd4e5f6a7-0002-4000-8000-000000000002', '1/4 Pollo Asado', 2, 15.00),
('a7b8c9d0-0005-4000-8000-000000000004', 'f6a7b8c9-0004-4000-8000-000000000004', 'd4e5f6a7-0006-4000-8000-000000000006', 'Inka Cola 1L', 1, 7.00),
('a7b8c9d0-0006-4000-8000-000000000005', 'f6a7b8c9-0005-4000-8000-000000000005', 'd4e5f6a7-0002-4000-8000-000000000002', '1/4 Pollo Asado', 1, 15.00)
ON CONFLICT (order_item_id) DO NOTHING;

-- KDS tickets
INSERT INTO kds_tickets (ticket_id, order_id, type, status, label, created_at) VALUES
('b8c9d0e1-0001-4000-8000-000000000001', 'f6a7b8c9-0001-4000-8000-000000000001', 'Normal', 'listo', 'Mesa 5 - Pollo a la Brasa',
 '2026-05-26 12:30:00-05'),
('b8c9d0e1-0002-4000-8000-000000000002', 'f6a7b8c9-0002-4000-8000-000000000002', 'Normal', 'en_preparacion', 'Mesa 8 - Anticuchos',
 '2026-05-26 12:45:00-05'),
('b8c9d0e1-0003-4000-8000-000000000003', 'f6a7b8c9-0003-4000-8000-000000000003', 'Urgente', 'nuevo', 'Mesa 3 - Combo Familiar',
 '2026-05-26 13:00:00-05'),
('b8c9d0e1-0004-4000-8000-000000000004', 'f6a7b8c9-0004-4000-8000-000000000004', 'Normal', 'listo', 'Mesa 2 - 1/4 Pollo x2',
 '2026-05-26 11:15:00-05')
ON CONFLICT (ticket_id) DO NOTHING;

-- 8. MERMAS
-- ============================================================
INSERT INTO mermas (merma_id, inventory_id, quantity, unit, reason, notes, registered_by) VALUES
('c9d0e1f2-0001-4000-8000-000000000001', 'e5f6a7b8-0003-4000-8000-000000000003', 2, 'unidades',
 'Producto vencido', 'Inka Cola 1L con fecha de expiración pasada', 'b2c3d4e5-0001-4000-8000-000000000001'),
('c9d0e1f2-0002-4000-8000-000000000002', 'e5f6a7b8-0002-4000-8000-000000000002', 1, 'unidades',
 'Rotura de stock', 'Se cayó y rompió el envase', 'b2c3d4e5-0001-4000-8000-000000000001')
ON CONFLICT (merma_id) DO NOTHING;

-- 9. NOTIFICACIONES
-- ============================================================
INSERT INTO notifications (notification_id, title, message, type, user_id) VALUES
('d0e1f2a3-0001-4000-8000-000000000001', 'Stock Crítico',
 'El producto "1/4 Pollo Asado" tiene stock crítico en Sede Central (3 unidades).', 'alert',
 'b2c3d4e5-0001-4000-8000-000000000001'),
('d0e1f2a3-0002-4000-8000-000000000002', 'Pedido Urgente',
 'Se registró un pedido urgente en KDS - Mesa 3.', 'warning',
 'b2c3d4e5-0001-4000-8000-000000000001'),
('d0e1f2a3-0003-4000-8000-000000000003', 'Nueva Merma',
 'Se registró una merma de Inka Cola 1L (2 unidades) por producto vencido.', 'info',
 'b2c3d4e5-0001-4000-8000-000000000001'),
('d0e1f2a3-0004-4000-8000-000000000004', 'Venta Completada',
 'Pedido Mesa 5 completado exitosamente - S/ 55.00', 'success', NULL)
ON CONFLICT (notification_id) DO NOTHING;
