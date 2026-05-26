from pydantic import BaseModel


class KpiResponse(BaseModel):
    total_sales_today: float
    total_orders_today: int
    critical_stock_count: int
    active_sedes: int


class TopProduct(BaseModel):
    name: str
    qty: int
    total: float
    pct: float


class RecentTransaction(BaseModel):
    id: str
    sede_name: str
    product: str
    amount: float
    time: str


class CategoryDistribution(BaseModel):
    name: str
    pct: float
    value: str
    color: str


class DashboardResponse(BaseModel):
    kpi: KpiResponse
    top_products: list[TopProduct]
    recent_transactions: list[RecentTransaction]
    category_distribution: list[CategoryDistribution]
