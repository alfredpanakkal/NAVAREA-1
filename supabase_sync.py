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
        sys.exit(0)  # Exit gracefully so the action doesn't fail if secrets aren't set yet
        
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
    
    if not warnings_to_insert:
        print("No warnings found in parsed_warnings.json to sync.")
        return

    print(f"Attempting to upsert {len(messages_to_insert)} records to 'raw_messages'...")
    try:
        supabase.table("raw_messages").upsert(messages_to_insert, on_conflict="warning_id,source_id").execute()
        print("Successfully synced to raw_messages.")
    except Exception as e:
        print(f"Failed to sync raw_messages: {e}")

    print(f"Attempting to upsert {len(warnings_to_insert)} records to 'nav_warnings'...")
    try:
        # Since 'spatial' is a dict (GeoJSON) and 'charts' is a list, supabase-py handles JSONB natively
        supabase.table("nav_warnings").upsert(warnings_to_insert, on_conflict="warning_id,source_id").execute()
        print("Successfully synced to nav_warnings.")
    except Exception as e:
        print(f"Failed to sync nav_warnings: {e}")
            
    print(f"Finished sync operation.")

if __name__ == "__main__":
    sync_to_supabase()
