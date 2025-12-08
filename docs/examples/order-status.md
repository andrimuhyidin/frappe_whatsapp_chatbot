# Example: Order Status

Check order status from the database using Script responses.

## Overview

Users can check their order status by entering an order ID.

## Flow Configuration

### Basic Settings

```
Flow Name: Order Status
Enabled: ✓
Trigger Keywords: order status, track order, my order, order
Initial Message: I can help you check your order status.
```

### Steps

#### Step 1: Ask Order ID

| Field | Value |
|-------|-------|
| Step Name | ask_order_id |
| Message | Please enter your Order ID (e.g., SAL-ORD-2024-00001) |
| Message Type | Text |
| Input Type | Text |
| Store As | order_id |

#### Step 2: Show Status (Script)

| Field | Value |
|-------|-------|
| Step Name | show_status |
| Message | Checking order... |
| Message Type | Script |
| Input Type | None |

**Response Script:**

```python
order_id = data.get('order_id', '').strip()

if not order_id:
    response = "No order ID provided. Please try again."
else:
    try:
        order = frappe.get_doc('Sales Order', order_id)

        # Format currency
        total = frappe.format_value(order.grand_total, {'fieldtype': 'Currency'})

        # Get delivery status
        delivery_status = "Not yet shipped"
        if order.per_delivered == 100:
            delivery_status = "Delivered"
        elif order.per_delivered > 0:
            delivery_status = f"Partially delivered ({order.per_delivered}%)"

        response = f"""📦 *Order Details*

Order ID: {order.name}
Date: {order.transaction_date}
Status: {order.status}

Items: {len(order.items)} item(s)
Total: {total}

Delivery: {delivery_status}
"""

        # Add delivery date if available
        if order.delivery_date:
            response += f"Expected Delivery: {order.delivery_date}"

    except frappe.DoesNotExistError:
        response = f"❌ Sorry, order '{order_id}' was not found.\n\nPlease check the order ID and try again."

    except Exception as e:
        frappe.log_error(f"Order lookup error: {str(e)}", "WhatsApp Chatbot")
        response = "⚠️ Sorry, I couldn't fetch the order details. Please try again later."
```

### Completion Settings

```
Completion Message: Is there anything else I can help you with? Type "help" for options.
```

## Conversation Flow

```
User: order status

Bot: I can help you check your order status.
Bot: Please enter your Order ID (e.g., SAL-ORD-2024-00001)

User: SAL-ORD-2024-00042

Bot: 📦 Order Details

     Order ID: SAL-ORD-2024-00042
     Date: 2024-01-15
     Status: To Deliver and Bill

     Items: 3 item(s)
     Total: ₹15,000.00

     Delivery: Not yet shipped
     Expected Delivery: 2024-01-20

Bot: Is there anything else I can help you with? Type "help" for options.
```

## Handling Invalid Orders

```
User: order status

Bot: Please enter your Order ID

User: ABC123

Bot: ❌ Sorry, order 'ABC123' was not found.
     Please check the order ID and try again.
```

## Enhancements

### Allow Order Lookup by Phone

If orders have customer phone numbers:

```python
order_id = data.get('order_id', '').strip()

# First try direct order ID lookup
order = None
try:
    order = frappe.get_doc('Sales Order', order_id)
except frappe.DoesNotExistError:
    pass

# If not found, try finding by phone number (last order)
if not order:
    orders = frappe.get_all(
        'Sales Order',
        filters={'contact_mobile': phone_number},
        fields=['name'],
        order_by='creation desc',
        limit=1
    )
    if orders:
        order = frappe.get_doc('Sales Order', orders[0].name)

if order:
    response = f"Order {order.name}: {order.status}"
else:
    response = "No orders found."
```

### Show Order Items

```python
items_list = []
for item in order.items[:5]:  # Show first 5 items
    items_list.append(f"• {item.item_name} x {item.qty}")

items_str = "\n".join(items_list)
if len(order.items) > 5:
    items_str += f"\n... and {len(order.items) - 5} more items"

response = f"""📦 Order {order.name}

Items:
{items_str}

Total: {total}
"""
```
