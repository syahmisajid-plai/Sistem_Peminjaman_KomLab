from .connection import get_client

supabase = get_client()


def insert_loan(user_id, item_name, start_date, end_date):
    return (
        supabase.table("loans")
        .insert(
            {
                "user_id": user_id,
                "item_name": item_name,
                "start_date": start_date,
                "end_date": end_date,
                "status": "dipinjam",
            }
        )
        .execute()
    )


def get_all_loans():
    return supabase.table("loans").select("*").execute()


def update_loan_status(loan_id, status):
    return (
        supabase.table("loans").update({"status": status}).eq("id", loan_id).execute()
    )
