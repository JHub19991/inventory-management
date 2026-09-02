"""
Tests for restocking API endpoints (recommendations and submitted orders).
"""
import pytest


class TestRestockRecommendationsEndpoint:
    """Test suite for GET /api/restock/recommendations."""

    def test_get_recommendations_structure(self, client):
        """Test the recommendation response has the expected shape."""
        response = client.get("/api/restock/recommendations?budget=50000")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        for field in ["budget", "total_cost", "remaining_budget", "item_count", "items"]:
            assert field in data

        assert data["budget"] == 50000
        assert isinstance(data["items"], list)
        assert data["item_count"] == len(data["items"])

        if data["items"]:
            item = data["items"][0]
            for field in [
                "item_sku", "item_name", "trend", "unit_cost", "lead_time_days",
                "current_demand", "forecasted_demand", "demand_gap",
                "recommended_quantity", "line_cost", "fully_funded",
            ]:
                assert field in item

    def test_recommendations_stay_within_budget(self, client):
        """Total cost must never exceed the requested budget."""
        for budget in [1000, 5000, 25000, 100000]:
            response = client.get(f"/api/restock/recommendations?budget={budget}")
            assert response.status_code == 200
            data = response.json()
            assert data["total_cost"] <= budget + 0.01
            assert data["remaining_budget"] >= -0.01
            assert abs(data["budget"] - data["total_cost"] - data["remaining_budget"]) < 0.01

    def test_recommendations_only_include_demand_gap_items(self, client):
        """Recommended items must have forecasted demand above current demand."""
        response = client.get("/api/restock/recommendations?budget=1000000")
        data = response.json()

        for item in data["items"]:
            assert item["forecasted_demand"] > item["current_demand"]
            assert item["demand_gap"] == item["forecasted_demand"] - item["current_demand"]
            assert item["recommended_quantity"] > 0

    def test_recommendations_line_cost_matches_quantity(self, client):
        """Each line cost should equal quantity times unit cost."""
        response = client.get("/api/restock/recommendations?budget=1000000")
        data = response.json()

        for item in data["items"]:
            expected = item["recommended_quantity"] * item["unit_cost"]
            assert abs(item["line_cost"] - expected) < 0.01

    def test_recommendations_prioritize_increasing_trend(self, client):
        """Increasing-trend items should be ranked ahead of other trends."""
        response = client.get("/api/restock/recommendations?budget=1000000")
        data = response.json()

        trends = [item["trend"].lower() for item in data["items"]]
        increasing_indexes = [i for i, t in enumerate(trends) if t == "increasing"]
        other_indexes = [i for i, t in enumerate(trends) if t != "increasing"]

        if increasing_indexes and other_indexes:
            assert max(increasing_indexes) < min(other_indexes)

    def test_large_budget_fully_funds_all_gap_items(self, client):
        """A very large budget funds every candidate item in full."""
        response = client.get("/api/restock/recommendations?budget=100000000")
        data = response.json()

        assert data["item_count"] > 0
        for item in data["items"]:
            assert item["fully_funded"] is True
            assert item["recommended_quantity"] == item["demand_gap"]

    def test_zero_budget_returns_no_items(self, client):
        """A zero budget yields an empty recommendation list."""
        response = client.get("/api/restock/recommendations?budget=0")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["item_count"] == 0

    def test_negative_budget_rejected(self, client):
        """A negative budget is a client error."""
        response = client.get("/api/restock/recommendations?budget=-500")
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_small_budget_partially_funds_last_item(self, client):
        """A tight budget partially funds the item that hits the ceiling."""
        response = client.get("/api/restock/recommendations?budget=500")
        data = response.json()

        assert data["total_cost"] <= 500 + 0.01
        if data["items"]:
            assert any(item["fully_funded"] is False for item in data["items"]) or \
                data["remaining_budget"] < min(i["unit_cost"] for i in data["items"])


class TestSubmittedOrdersEndpoints:
    """Test suite for GET/POST /api/orders/submitted."""

    def test_get_submitted_orders_returns_list(self, client):
        """The submitted orders endpoint always returns a list."""
        response = client.get("/api/orders/submitted")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_submitted_order(self, client):
        """Posting a budget creates a restock order with the recommended items."""
        response = client.post("/api/orders/submitted", json={"budget": 60000})
        assert response.status_code == 201

        order = response.json()
        for field in [
            "id", "order_number", "status", "budget", "total_value",
            "submitted_date", "expected_delivery", "max_lead_time_days", "items",
        ]:
            assert field in order

        assert order["status"] == "Submitted"
        assert order["budget"] == 60000
        assert order["order_number"].startswith("RST-")
        assert order["total_value"] <= 60000 + 0.01
        assert len(order["items"]) > 0

        for item in order["items"]:
            for field in [
                "item_sku", "item_name", "quantity", "unit_cost",
                "line_cost", "lead_time_days",
            ]:
                assert field in item
            assert item["quantity"] > 0

        assert order["max_lead_time_days"] == max(i["lead_time_days"] for i in order["items"])

    def test_created_order_appears_in_submitted_list(self, client):
        """A created order shows up in the submitted orders list."""
        created = client.post("/api/orders/submitted", json={"budget": 45000}).json()

        listing = client.get("/api/orders/submitted").json()
        order_numbers = [o["order_number"] for o in listing]
        assert created["order_number"] in order_numbers

    def test_submitted_list_is_newest_first(self, client):
        """The submitted list returns the most recently created order first."""
        first = client.post("/api/orders/submitted", json={"budget": 30000}).json()
        second = client.post("/api/orders/submitted", json={"budget": 35000}).json()

        listing = client.get("/api/orders/submitted").json()
        numbers = [o["order_number"] for o in listing]
        assert numbers.index(second["order_number"]) < numbers.index(first["order_number"])

    def test_expected_delivery_after_submitted_date(self, client):
        """Expected delivery must be later than the submitted date."""
        order = client.post("/api/orders/submitted", json={"budget": 50000}).json()
        assert order["expected_delivery"] > order["submitted_date"]

    def test_zero_budget_rejected(self, client):
        """A zero or negative budget cannot create an order."""
        assert client.post("/api/orders/submitted", json={"budget": 0}).status_code == 400
        assert client.post("/api/orders/submitted", json={"budget": -100}).status_code == 400

    def test_tiny_budget_rejected(self, client):
        """A budget too small to buy any item returns a client error."""
        response = client.post("/api/orders/submitted", json={"budget": 1})
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_missing_budget_is_validation_error(self, client):
        """Omitting the budget field is a 422 validation error."""
        response = client.post("/api/orders/submitted", json={})
        assert response.status_code == 422
