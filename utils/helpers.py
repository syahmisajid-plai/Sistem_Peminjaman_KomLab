from datetime import datetime


def format_tanggal(date_obj):
    """Ubah datetime ke format DD-MM-YYYY."""
    if isinstance(date_obj, datetime):
        return date_obj.strftime("%d-%m-%Y")
    return str(date_obj)


def status_label(status: str):
    """Mapping status ke label lebih ramah."""
    mapping = {
        "pending": "⏳ Menunggu",
        "approved": "✅ Disetujui",
        "rejected": "❌ Ditolak",
        "returned": "📦 Dikembalikan",
    }
    return mapping.get(status, status)
