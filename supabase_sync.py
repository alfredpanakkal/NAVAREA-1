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
        sys.exit(0)
        
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

    # 1. Sync raw_messages via insert
    print(f"Syncing {len(messages_to_insert)} records to 'raw_messages'...")
    for msg in messages_to_insert:
        try:
            print(f"  [raw_messages] Inserting record {msg['warning_id']}...")
            supabase.table("raw_messages").insert(msg).execute()
            print(f"  [raw_messages] Successfully inserted {msg['warning_id']}.")
        except Exception as e:
            # If already exists or duplicate error, print warning and continue
            print(f"  [raw_messages] Note on {msg['warning_id']}: {e}")

    # 2. Sync nav_warnings via upsert (on composite key warning_id, source_id)
    print(f"Syncing {len(warnings_to_insert)} records to 'nav_warnings'...")
    for warn in warnings_to_insert:
        try:
            print(f"  [nav_warnings] Upserting record {warn['warning_id']}...")
            supabase.table("nav_warnings").upsert(warn, on_conflict="warning_id,source_id").execute()
            print(f"  [nav_warnings] Successfully upserted {warn['warning_id']}.")
        except Exception as e:
            print(f"  [nav_warnings] ERROR syncing {warn['warning_id']}: {e}")
            has_errors = True

    if has_errors:
        print("Sync completed with errors.")
        sys.exit(1)
    else:
        print("Finished sync operation cleanly with 0 errors!")

if __name__ == "__main__":
    sync_to_supabase()
