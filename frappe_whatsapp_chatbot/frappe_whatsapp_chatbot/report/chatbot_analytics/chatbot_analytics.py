# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days, today, flt, time_diff_in_seconds


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart(data, filters)
	summary = get_summary(filters)
	
	return columns, data, None, chart, summary


def get_columns(filters):
	group_by = filters.get("group_by", "date")
	
	columns = []
	
	if group_by == "date":
		columns.append({
			"label": _("Date"),
			"fieldname": "group_field",
			"fieldtype": "Date",
			"width": 120
		})
	elif group_by == "flow":
		columns.append({
			"label": _("Flow"),
			"fieldname": "group_field",
			"fieldtype": "Link",
			"options": "WhatsApp Chatbot Flow",
			"width": 200
		})
	elif group_by == "response_type":
		columns.append({
			"label": _("Response Type"),
			"fieldname": "group_field",
			"fieldtype": "Data",
			"width": 150
		})
	
	columns.extend([
		{
			"label": _("Total Sessions"),
			"fieldname": "total_sessions",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Completed"),
			"fieldname": "completed",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Agent Transfers"),
			"fieldname": "agent_transfers",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Completion Rate (%)"),
			"fieldname": "completion_rate",
			"fieldtype": "Percent",
			"width": 130
		},
		{
			"label": _("Total Messages"),
			"fieldname": "total_messages",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Avg Messages/Session"),
			"fieldname": "avg_messages",
			"fieldtype": "Float",
			"precision": 1,
			"width": 140
		}
	])
	
	return columns


def get_data(filters):
	conditions = get_conditions(filters)
	group_by = filters.get("group_by", "date")
	
	if group_by == "date":
		group_field = "DATE(creation)"
	elif group_by == "flow":
		group_field = "current_flow"
	elif group_by == "response_type":
		group_field = "COALESCE(last_response_type, 'Unknown')"
	else:
		group_field = "DATE(creation)"
	
	# Check if session doctype exists
	if not frappe.db.exists("DocType", "WhatsApp Chatbot Session"):
		# Fallback to message-based analytics
		return get_message_based_data(filters)
	
	query = """
		SELECT
			{group_field} as group_field,
			COUNT(*) as total_sessions,
			SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
			SUM(CASE WHEN transferred_to_agent = 1 THEN 1 ELSE 0 END) as agent_transfers,
			SUM(message_count) as total_messages,
			AVG(message_count) as avg_messages
		FROM `tabWhatsApp Chatbot Session`
		WHERE 1=1
		{conditions}
		GROUP BY {group_field}
		ORDER BY total_sessions DESC
	""".format(group_field=group_field, conditions=conditions)
	
	try:
		data = frappe.db.sql(query, filters, as_dict=True)
	except Exception:
		return get_message_based_data(filters)
	
	# Calculate completion rate
	for row in data:
		total = row.get("total_sessions") or 0
		completed = row.get("completed") or 0
		row["completion_rate"] = round((completed / total * 100) if total > 0 else 0, 2)
		row["avg_messages"] = round(row.get("avg_messages") or 0, 1)
	
	return data


def get_message_based_data(filters):
	"""Fallback analytics based on WhatsApp Message."""
	conditions = get_conditions_messages(filters)
	
	query = """
		SELECT
			DATE(creation) as group_field,
			COUNT(DISTINCT `from`) as total_sessions,
			COUNT(*) as total_messages,
			COUNT(*) / COUNT(DISTINCT `from`) as avg_messages,
			0 as completed,
			0 as agent_transfers,
			0 as completion_rate
		FROM `tabWhatsApp Message`
		WHERE type = 'Incoming'
		{conditions}
		GROUP BY DATE(creation)
		ORDER BY group_field DESC
	""".format(conditions=conditions)
	
	data = frappe.db.sql(query, filters, as_dict=True)
	
	for row in data:
		row["avg_messages"] = round(row.get("avg_messages") or 0, 1)
	
	return data


def get_conditions(filters):
	conditions = []
	
	if filters.get("from_date"):
		conditions.append("AND creation >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("AND creation <= %(to_date)s")
	
	return " ".join(conditions)


def get_conditions_messages(filters):
	conditions = []
	
	if filters.get("from_date"):
		conditions.append("AND creation >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("AND creation <= %(to_date)s")
	
	return " ".join(conditions)


def get_chart(data, filters):
	if not data:
		return None
	
	labels = [str(row.get("group_field") or "Unknown") for row in data[:30]]
	sessions = [row.get("total_sessions") or 0 for row in data[:30]]
	completed = [row.get("completed") or 0 for row in data[:30]]
	
	group_by = filters.get("group_by", "date")
	chart_type = "line" if group_by == "date" else "bar"
	
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": _("Total Sessions"),
					"values": sessions
				},
				{
					"name": _("Completed"),
					"values": completed
				}
			]
		},
		"type": chart_type,
		"colors": ["#5e64ff", "#28a745"]
	}


def get_summary(filters):
	conditions = get_conditions(filters)
	
	# Try session-based summary
	try:
		if frappe.db.exists("DocType", "WhatsApp Chatbot Session"):
			summary_data = frappe.db.sql("""
				SELECT
					COUNT(*) as total_sessions,
					SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
					SUM(CASE WHEN transferred_to_agent = 1 THEN 1 ELSE 0 END) as agent_transfers,
					SUM(message_count) as total_messages,
					AVG(message_count) as avg_messages
				FROM `tabWhatsApp Chatbot Session`
				WHERE 1=1
				{conditions}
			""".format(conditions=conditions), filters, as_dict=True)[0]
		else:
			raise Exception("Fallback to message-based")
	except Exception:
		# Fallback to message-based
		summary_data = frappe.db.sql("""
			SELECT
				COUNT(DISTINCT `from`) as total_sessions,
				COUNT(*) as total_messages,
				COUNT(*) / NULLIF(COUNT(DISTINCT `from`), 0) as avg_messages,
				0 as completed,
				0 as agent_transfers
			FROM `tabWhatsApp Message`
			WHERE type = 'Incoming'
			{conditions}
		""".format(conditions=get_conditions_messages(filters)), filters, as_dict=True)[0]
	
	total = summary_data.get("total_sessions") or 0
	completed = summary_data.get("completed") or 0
	completion_rate = (completed / total * 100) if total > 0 else 0
	
	return [
		{
			"value": total,
			"label": _("Total Sessions"),
			"datatype": "Int"
		},
		{
			"value": completed,
			"label": _("Completed"),
			"datatype": "Int",
			"indicator": "green"
		},
		{
			"value": summary_data.get("agent_transfers") or 0,
			"label": _("Agent Transfers"),
			"datatype": "Int",
			"indicator": "orange"
		},
		{
			"value": round(completion_rate, 1),
			"label": _("Completion Rate (%)"),
			"datatype": "Percent"
		},
		{
			"value": summary_data.get("total_messages") or 0,
			"label": _("Total Messages"),
			"datatype": "Int"
		}
	]
