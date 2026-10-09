import os
import json
import sys
from supabase import create_client, Client

def sync_to_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL or SUPABASE_KEY environment variables are missing.")
        print("Skipping Supabase sync.")
        sys.exit(0)  # Exit gracefully if secrets aren't set yet
        
    try:
        supabase: Client = create_client(url, key)
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        sys.exit(1)

    try:
        with open("parsed_warnings.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: parsed_warnings.json not found.")
        sys.exit(1)

    messages_to_insert = data.get("raw_messages", [])
    warnings_to_insert = data.get("nav_warnings", [])
    
    if not warnings_to_insert and not messages_to_insert:
        print("No warnings found in parsed_warnings.json to sync.")
        return

    has_errors = False

    # 1. Sync raw_messages
    print(f"Syncing {len(messages_to_insert)} records to 'raw_messages'...")
    for msg in messages_to_insert:
        try:
            # Check if record already exists by warning_id and source_id
            existing = supabase.table("raw_messages").select("message_id").eq("warning_id", msg["warning_id"]).eq("source_id", msg["source_id"]).execute()
            if existing.data and len(existing.data) > 0:
                print(f"  [raw_messages] Record {msg['warning_id']} exists. Updating...")
                supabase.table("raw_messages").update(msg).eq("message_id", existing.data[0]["message_id"]).execute()
            else:
                print(f"  [raw_messages] Inserting new record {msg['warning_id']}...")
                supabase.table("raw_messages").insert(msg).execute()
        except Exception as e:
            print(f"  [raw_messages] ERROR syncing {msg['warning_id']}: {e}")
            has_errors = True

    # 2. Sync nav_warnings
    print(f"Syncing {len(warnings_to_insert)} records to 'nav_warnings'...")
    for warn in warnings_to_insert:
        try:
            # Check if record already exists by warning_id and source_id
            existing = supabase.table("nav_warnings").select("id").eq("warning_id", warn["warning_id"]).eq("source_id", warn["source_id"]).execute()
            if existing.data and len(existing.data) > 0:
                print(f"  [nav_warnings] Record {warn['warning_id']} exists. Updating...")
                supabase.table("nav_warnings").update(warn).eq("id", existing.data[0]["id"]).execute()
            else:
                print(f"  [nav_warnings] Inserting new record {warn['warning_id']}...")
                supabase.table("nav_warnings").insert(warn).execute()
        except Exception as e:
            print(f"  [nav_warnings] ERROR syncing {warn['warning_id']}: {e}")
            has_errors = True

    if has_errors:
        print("Sync completed with errors. Failing step.")
        sys.exit(1)
    else:
        print("Finished sync operation cleanly with 0 errors!")

if __name__ == "__main__":
    sync_to_supabase()
