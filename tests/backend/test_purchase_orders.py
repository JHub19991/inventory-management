"""
Tests for purchase order API endpoints.

  POST /api/purchase-orders
  GET  /api/purchase-orders/{backlog_item_id}

These tests share module-level state (the in-memory purchase_orders list), so
they are written to run in definition order: the first test creates a purchase
order for backlog item "1" and later tests build on that.
"""
import pytest


def _po_payload(**overrides):
    payload = {
        "backlog_item_id": "1",
        "supplier_name": "Acme Supply Co",
        "quantity": 350,
        "unit_cost": 12.5,
        "expected_delivery_date": "2025-12-15",
        "notes": "Rush order for shortage",
    }
    payload.update(overrides)
    return payload


class TestPurchaseOrderEndpoints:
    """Test suite for purchase order creation and lookup."""

    def test_create_purchase_order(self, client):
        """Posting a valid payload creates a purchase order."""
        response = client.post("/api/purchase-orders", json=_po_payload())
        assert response.status_code == 201

        po = response.json()
        for field in [
            "id", "backlog_item_id", "supplier_name", "quantity", "unit_cost",
            "expected_delivery_date", "status", "created_date", "notes",
        ]:
            assert field in po

        assert po["backlog_item_id"] == "1"
        assert po["supplier_name"] == "Acme Supply Co"
        assert po["quantity"] == 350
        assert po["status"] == "Pending"
        assert po["id"].startswith("PO-")

    def test_backlog_item_reflects_purchase_order(self, client):
        """The backlog listing exposes the linked purchase order id."""
        backlog = client.get("/api/backlog").json()
        item = next(b for b in backlog if b["id"] == "1")
        assert item["has_purchase_order"] is True
        assert item["purchase_order_id"] is not None
        assert item["purchase_order_id"].startswith("PO-")

    def test_get_purchase_order_by_backlog_item(self, client):
        """The purchase order can be fetched by its backlog item id."""
        response = client.get("/api/purchase-orders/1")
        assert response.status_code == 200
        assert response.json()["backlog_item_id"] == "1"

    def test_duplicate_purchase_order_rejected(self, client):
        """A backlog item can only have one purchase order."""
        response = client.post("/api/purchase-orders", json=_po_payload())
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_purchase_order_unknown_backlog_item(self, client):
        """Creating a PO for a nonexistent backlog item returns 404."""
        response = client.post(
            "/api/purchase-orders", json=_po_payload(backlog_item_id="nonexistent-999")
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_purchase_order_none_exists(self, client):
        """Looking up a backlog item with no purchase order returns 404."""
        response = client.get("/api/purchase-orders/4")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_purchase_order_invalid_quantity(self, client):
        """A non-positive quantity is a client error."""
        response = client.post(
            "/api/purchase-orders", json=_po_payload(backlog_item_id="2", quantity=0)
        )
        assert response.status_code == 400
        assert "quantity" in response.json()["detail"].lower()

    def test_create_purchase_order_negative_unit_cost(self, client):
        """A negative unit cost is a client error."""
        response = client.post(
            "/api/purchase-orders", json=_po_payload(backlog_item_id="3", unit_cost=-5)
        )
        assert response.status_code == 400
        assert "unit cost" in response.json()["detail"].lower()

    def test_create_purchase_order_missing_fields(self, client):
        """Omitting required fields is a 422 validation error."""
        response = client.post(
            "/api/purchase-orders", json={"backlog_item_id": "2"}
        )
        assert response.status_code == 422
