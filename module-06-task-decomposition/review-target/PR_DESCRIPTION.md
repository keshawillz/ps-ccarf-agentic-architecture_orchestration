# PR 218: Add refund status endpoint and order listing

Adds `get_refund_status` and `list_orders`. Both follow the existing
handler pattern.

Files changed: api/refunds_api.py, api/orders_api.py,
services/refund_service.py, services/order_service.py, services/audit.py
