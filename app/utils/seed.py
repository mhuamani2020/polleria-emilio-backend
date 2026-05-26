"""
Script para poblar la base de datos con datos de prueba.
Ejecutar: python -m app.utils.seed
"""
import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.sede import Sede
from app.models.user import User
from app.models.category import Category
from app.models.product import Product, ComboItem
from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.models.kds_ticket import KdsTicket
from app.models.merma import Merma
from app.models.notification import Notification


async def seed():
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(Sede).limit(1))
        if existing.scalar_one_or_none():
            print("La base de datos ya tiene datos. Omitiendo seed.")
            return

        sede_central_id = uuid.UUID("a1b2c3d4-0001-4000-8000-000000000001")
        sede_norte_id = uuid.UUID("a1b2c3d4-0002-4000-8000-000000000002")
        sede_sur_id = uuid.UUID("a1b2c3d4-0003-4000-8000-000000000003")

        sedes = [
            Sede(sede_id=sede_central_id, name="Sede Central", address="Av. La Marina 1234",
                 phone="999-111-222", manager="Carlos López", status="Activa", sales=28500),
            Sede(sede_id=sede_norte_id, name="Sede Norte", address="Jr. Los Olivos 567",
                 phone="999-333-444", manager="María García", status="Activa", sales=19300),
            Sede(sede_id=sede_sur_id, name="Sede Sur", address="Av. Benavides 890",
                 phone="999-555-666", manager="José Martínez", status="Inactiva", sales=0),
        ]
        db.add_all(sedes)
        await db.flush()

        admin_id = uuid.UUID("b2c3d4e5-0001-4000-8000-000000000001")
        cajero_id = uuid.UUID("b2c3d4e5-0002-4000-8000-000000000002")
        mesero_id = uuid.UUID("b2c3d4e5-0003-4000-8000-000000000003")
        cajero_norte_id = uuid.UUID("b2c3d4e5-0004-4000-8000-000000000004")

        password = hash_password("Polleria123!")
        users = [
            User(user_id=admin_id, username="admin.central", password_hash=password,
                 display_name="Admin Central", dni="12345678", phone="999-000-111",
                 shift="Mañana", role="admin", sede_id=sede_central_id),
            User(user_id=cajero_id, username="cajero.central", password_hash=password,
                 display_name="Cajero Central", dni="23456789", phone="999-000-222",
                 shift="Tarde", role="cajero", sede_id=sede_central_id),
            User(user_id=mesero_id, username="mesero.central", password_hash=password,
                 display_name="Mesero Central", dni="34567890", phone="999-000-333",
                 shift="Noche", role="mesero", sede_id=sede_central_id),
            User(user_id=cajero_norte_id, username="cajero.norte", password_hash=password,
                 display_name="Cajero Norte", dni="45678901", phone="999-000-444",
                 shift="Mañana", role="cajero", sede_id=sede_norte_id),
        ]
        db.add_all(users)
        await db.flush()

        cat_parr = uuid.UUID("c3d4e5f6-0001-4000-8000-000000000001")
        cat_beb = uuid.UUID("c3d4e5f6-0002-4000-8000-000000000002")
        cat_ent = uuid.UUID("c3d4e5f6-0003-4000-8000-000000000003")
        cat_com = uuid.UUID("c3d4e5f6-0004-4000-8000-000000000004")
        cat_ins = uuid.UUID("c3d4e5f6-0005-4000-8000-000000000005")

        categories = [
            Category(category_id=cat_parr, name="Parrilladas", description="Platos a la parrilla"),
            Category(category_id=cat_beb, name="Bebidas", description="Bebidas frías y calientes"),
            Category(category_id=cat_ent, name="Entradas", description="Entradas y aperitivos"),
            Category(category_id=cat_com, name="Combos", description="Combos promocionales"),
            Category(category_id=cat_ins, name="Insumos", description="Insumos de cocina"),
        ]
        db.add_all(categories)
        await db.flush()

        prod1 = uuid.UUID("d4e5f6a7-0001-4000-8000-000000000001")
        prod2 = uuid.UUID("d4e5f6a7-0002-4000-8000-000000000002")
        prod3 = uuid.UUID("d4e5f6a7-0003-4000-8000-000000000003")
        prod4 = uuid.UUID("d4e5f6a7-0004-4000-8000-000000000004")
        prod5 = uuid.UUID("d4e5f6a7-0005-4000-8000-000000000005")
        prod6 = uuid.UUID("d4e5f6a7-0006-4000-8000-000000000006")
        prod7 = uuid.UUID("d4e5f6a7-0007-4000-8000-000000000007")
        prod8 = uuid.UUID("d4e5f6a7-0008-4000-8000-000000000008")
        prod9 = uuid.UUID("d4e5f6a7-0009-4000-8000-000000000009")
        comb1 = uuid.UUID("d4e5f6a7-0010-4000-8000-000000000010")
        comb2 = uuid.UUID("d4e5f6a7-0011-4000-8000-000000000011")

        products = [
            Product(product_id=prod1, name="Pollo Entero Asado", price=45, icon="set_meal", category_id=cat_parr),
            Product(product_id=prod2, name="1/4 Pollo Asado", price=15, icon="restaurant", category_id=cat_parr),
            Product(product_id=prod3, name="Pollo a la Brasa", description="Pollo a la brasa con ensalada y papas",
                    price=55, icon="local_fire_department", category_id=cat_parr),
            Product(product_id=prod4, name="Anticuchos (4 und)", price=25, icon="skillet", category_id=cat_parr),
            Product(product_id=prod5, name="Papa Rellena", price=8, icon="lunch_dining", category_id=cat_ent),
            Product(product_id=prod6, name="Inka Cola 1L", price=7, icon="liquor", category_id=cat_beb),
            Product(product_id=prod7, name="Agua Mineral 500ml", price=3, icon="water_drop", category_id=cat_beb),
            Product(product_id=prod8, name="Causa Rellena", price=18, icon="tapas", category_id=cat_ent),
            Product(product_id=prod9, name="Papa a la Huancaína", price=12, icon="tapas", category_id=cat_ent),
            Product(product_id=comb1, name="Combo Familiar", price=59, icon="diversity_1",
                    category_id=cat_com, is_combo=True),
            Product(product_id=comb2, name="Combo Pareja", price=39, icon="favorite",
                    category_id=cat_com, is_combo=True),
        ]
        db.add_all(products)
        await db.flush()

        combo_items = [
            ComboItem(combo_id=comb1, product_id=prod1, qty=1),
            ComboItem(combo_id=comb1, product_id=prod6, qty=1),
            ComboItem(combo_id=comb2, product_id=prod2, qty=2),
            ComboItem(combo_id=comb2, product_id=prod6, qty=2),
        ]
        db.add_all(combo_items)
        await db.flush()

        inv_ids = [
            uuid.UUID("e5f6a7b8-0001-4000-8000-000000000001"),
            uuid.UUID("e5f6a7b8-0002-4000-8000-000000000002"),
            uuid.UUID("e5f6a7b8-0003-4000-8000-000000000003"),
            uuid.UUID("e5f6a7b8-0004-4000-8000-000000000004"),
            uuid.UUID("e5f6a7b8-0005-4000-8000-000000000005"),
            uuid.UUID("e5f6a7b8-0006-4000-8000-000000000006"),
        ]

        inventory = [
            Inventory(inventory_id=inv_ids[0], product_id=prod1, sede_id=sede_central_id,
                      current_stock=15, minimum_stock=5, unit="unidades", status="Óptimo"),
            Inventory(inventory_id=inv_ids[1], product_id=prod2, sede_id=sede_central_id,
                      current_stock=3, minimum_stock=5, unit="unidades", status="Crítico"),
            Inventory(inventory_id=inv_ids[2], product_id=prod6, sede_id=sede_central_id,
                      current_stock=8, minimum_stock=10, unit="unidades", status="Precaución"),
            Inventory(inventory_id=inv_ids[3], product_id=prod5, sede_id=sede_central_id,
                      current_stock=25, minimum_stock=10, unit="unidades", status="Óptimo"),
            Inventory(inventory_id=inv_ids[4], product_id=prod1, sede_id=sede_norte_id,
                      current_stock=10, minimum_stock=5, unit="unidades", status="Óptimo"),
            Inventory(inventory_id=inv_ids[5], product_id=prod6, sede_id=sede_norte_id,
                      current_stock=2, minimum_stock=5, unit="unidades", status="Crítico"),
        ]
        db.add_all(inventory)
        await db.flush()

        order_ids = [
            uuid.UUID("f6a7b8c9-0001-4000-8000-000000000001"),
            uuid.UUID("f6a7b8c9-0002-4000-8000-000000000002"),
            uuid.UUID("f6a7b8c9-0003-4000-8000-000000000003"),
            uuid.UUID("f6a7b8c9-0004-4000-8000-000000000004"),
            uuid.UUID("f6a7b8c9-0005-4000-8000-000000000005"),
        ]

        orders = [
            Order(order_id=order_ids[0], sede_id=sede_central_id, user_id=cajero_id,
                  status="entregado", total=55),
            Order(order_id=order_ids[1], sede_id=sede_central_id, user_id=cajero_id,
                  status="en_preparacion", total=25),
            Order(order_id=order_ids[2], sede_id=sede_central_id, user_id=cajero_id,
                  status="pendiente", total=59),
            Order(order_id=order_ids[3], sede_id=sede_norte_id, user_id=cajero_norte_id,
                  status="entregado", total=37),
            Order(order_id=order_ids[4], sede_id=sede_norte_id, user_id=cajero_norte_id,
                  status="pendiente", total=15),
        ]
        db.add_all(orders)
        await db.flush()

        order_items = [
            OrderItem(order_id=order_ids[0], product_id=prod3, product_name="Pollo a la Brasa", qty=1, unit_price=55, subtotal=55),
            OrderItem(order_id=order_ids[1], product_id=prod4, product_name="Anticuchos (4 und)", qty=1, unit_price=25, subtotal=25),
            OrderItem(order_id=order_ids[2], product_id=comb1, product_name="Combo Familiar", qty=1, unit_price=59, subtotal=59),
            OrderItem(order_id=order_ids[3], product_id=prod2, product_name="1/4 Pollo Asado", qty=2, unit_price=15, subtotal=30),
            OrderItem(order_id=order_ids[3], product_id=prod6, product_name="Inka Cola 1L", qty=1, unit_price=7, subtotal=7),
            OrderItem(order_id=order_ids[4], product_id=prod2, product_name="1/4 Pollo Asado", qty=1, unit_price=15, subtotal=15),
        ]
        db.add_all(order_items)
        await db.flush()

        ticket_ids = [
            uuid.UUID("b8c9d0e1-0001-4000-8000-000000000001"),
            uuid.UUID("b8c9d0e1-0002-4000-8000-000000000002"),
            uuid.UUID("b8c9d0e1-0003-4000-8000-000000000003"),
            uuid.UUID("b8c9d0e1-0004-4000-8000-000000000004"),
        ]

        tickets = [
            KdsTicket(ticket_id=ticket_ids[0], order_id=order_ids[0], type="Normal", status="listo", label="Mesa 5 - Pollo a la Brasa"),
            KdsTicket(ticket_id=ticket_ids[1], order_id=order_ids[1], type="Normal", status="en_preparacion", label="Mesa 8 - Anticuchos"),
            KdsTicket(ticket_id=ticket_ids[2], order_id=order_ids[2], type="Urgente", status="nuevo", label="Mesa 3 - Combo Familiar"),
            KdsTicket(ticket_id=ticket_ids[3], order_id=order_ids[3], type="Normal", status="listo", label="Mesa 2 - 1/4 Pollo x2"),
        ]
        db.add_all(tickets)
        await db.flush()

        mermas = [
            Merma(inventory_id=inv_ids[2], quantity=2, unit="unidades",
                  reason="Producto vencido", notes="Inka Cola 1L con fecha de expiración pasada",
                  registered_by=admin_id),
            Merma(inventory_id=inv_ids[1], quantity=1, unit="unidades",
                  reason="Rotura de stock", notes="Se cayó y rompió el envase",
                  registered_by=admin_id),
        ]
        db.add_all(mermas)
        await db.flush()

        notif_ids = [
            uuid.UUID("d0e1f2a3-0001-4000-8000-000000000001"),
            uuid.UUID("d0e1f2a3-0002-4000-8000-000000000002"),
            uuid.UUID("d0e1f2a3-0003-4000-8000-000000000003"),
            uuid.UUID("d0e1f2a3-0004-4000-8000-000000000004"),
        ]

        notifications = [
            Notification(notification_id=notif_ids[0], title="Stock Crítico",
                         message='El producto "1/4 Pollo Asado" tiene stock crítico en Sede Central (3 unidades).',
                         type="alert", user_id=admin_id),
            Notification(notification_id=notif_ids[1], title="Pedido Urgente",
                         message="Se registró un pedido urgente en KDS - Mesa 3.",
                         type="warning", user_id=admin_id),
            Notification(notification_id=notif_ids[2], title="Nueva Merma",
                         message="Se registró una merma de Inka Cola 1L (2 unidades) por producto vencido.",
                         type="info", user_id=admin_id),
            Notification(notification_id=notif_ids[3], title="Venta Completada",
                         message="Pedido Mesa 5 completado exitosamente - S/ 55.00",
                         type="success", user_id=None),
        ]
        db.add_all(notifications)

        await db.commit()
        print("Seed completado exitosamente.")


if __name__ == "__main__":
    asyncio.run(seed())
