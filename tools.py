

from langchain.tools import tool
from database import orders,products



@tool
def track_order(order_id: str) -> str:
    """
    Track the status of an order by its ID.
    """
    for order in orders:
        if order["order_id"] == order_id:
            return f"Order {order_id} status is {order['status']}."
    return f"Order {order_id} not found."




@tool
def cancel_order(order_id: str) -> str:
    """Cancel an order using order id."""

    for order in orders:
        if order["order_id"] == order_id:
            if order["status"] == "Delivered":
                return "Delivered order cannot be cancelled"

            order["status"] = "Cancelled"
            return f"Order {order_id} cancelled successfully"

    return "Order not found"



@tool
def refund_status(order_id: str) -> str:
    """Check refund status."""

    for order in orders:
        if order["order_id"] == order_id:
            return f"Refund status: {order['refund']}"

    return "Order not found"


@tool
def recommend_products(category: str) -> str:
    """Recommend products to users."""

    recommendations = []

    for product in products:
        recommendations.append(
            f"{product['name']} - Rs.{product['price']}"
        )

    return "\n".join(recommendations)


@tool
def escalate_to_human(issue: str) -> str:
    """Escalate issue to human support."""

    return f"Issue escalated to human agent: {issue}"



