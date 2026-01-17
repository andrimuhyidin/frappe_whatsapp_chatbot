"""Knowledge Base Admin API."""
import frappe
from frappe import _
import csv
from io import StringIO


@frappe.whitelist()
def export_knowledge_base():
    """Export all Knowledge Base entries as CSV."""
    kb_entries = frappe.get_all(
        "WhatsApp Knowledge Base",
        fields=["topic", "keywords", "content", "category", "is_active"],
        order_by="category, topic"
    )
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["topic", "keywords", "content", "category", "is_active"])
    writer.writeheader()
    writer.writerows(kb_entries)
    
    return {
        "data": output.getvalue(),
        "filename": "whatsapp_knowledge_base.csv"
    }


@frappe.whitelist()
def import_knowledge_base(csv_data):
    """Import Knowledge Base entries from CSV."""
    if not csv_data:
        frappe.throw(_("No CSV data provided"))
    
    reader = csv.DictReader(StringIO(csv_data))
    imported = 0
    updated = 0
    errors = []
    
    for row in reader:
        try:
            topic = row.get("topic", "").strip()
            if not topic:
                continue
            
            # Check for existing entry
            existing = frappe.db.get_value("WhatsApp Knowledge Base", {"topic": topic}, "name")
            
            if existing:
                # Update existing
                doc = frappe.get_doc("WhatsApp Knowledge Base", existing)
                doc.keywords = row.get("keywords", "")
                doc.content = row.get("content", "")
                doc.category = row.get("category", "")
                doc.is_active = row.get("is_active", "1") == "1"
                doc.save(ignore_permissions=True)
                updated += 1
            else:
                # Create new
                doc = frappe.new_doc("WhatsApp Knowledge Base")
                doc.topic = topic
                doc.keywords = row.get("keywords", "")
                doc.content = row.get("content", "")
                doc.category = row.get("category", "")
                doc.is_active = row.get("is_active", "1") == "1"
                doc.insert(ignore_permissions=True)
                imported += 1
                
        except Exception as e:
            errors.append(f"Error on row '{topic}': {str(e)}")
    
    frappe.db.commit()
    
    return {
        "imported": imported,
        "updated": updated,
        "errors": errors
    }


@frappe.whitelist()
def find_duplicates():
    """Find duplicate topics or overlapping keywords."""
    kb_entries = frappe.get_all(
        "WhatsApp Knowledge Base",
        fields=["name", "topic", "keywords"],
        filters={"is_active": 1}
    )
    
    duplicates = []
    keyword_map = {}
    
    for entry in kb_entries:
        # Check topic duplicates (case-insensitive)
        topic_lower = entry.topic.lower().strip()
        
        # Check keyword overlaps
        if entry.keywords:
            keywords = [k.strip().lower() for k in entry.keywords.split(",") if k.strip()]
            for kw in keywords:
                if kw in keyword_map:
                    duplicates.append({
                        "type": "keyword_overlap",
                        "keyword": kw,
                        "entries": [keyword_map[kw], entry.name]
                    })
                else:
                    keyword_map[kw] = entry.name
    
    return duplicates


@frappe.whitelist()
def bulk_update_keywords(entries):
    """Bulk update keywords for multiple entries."""
    if isinstance(entries, str):
        entries = frappe.parse_json(entries)
    
    updated = 0
    for entry in entries:
        name = entry.get("name")
        keywords = entry.get("keywords")
        
        if name and keywords is not None:
            frappe.db.set_value("WhatsApp Knowledge Base", name, "keywords", keywords)
            updated += 1
    
    frappe.db.commit()
    return {"updated": updated}
