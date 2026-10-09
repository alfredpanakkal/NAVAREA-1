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

    warnings_to_insert = data.get("nav_warnings", [])
    
    if not warnings_to_insert:
        print("No nav_warnings found in parsed_warnings.json to sync.")
        return

    print(f"Attempting to upsert {len(warnings_to_insert)} warnings to Supabase table 'navarea_one_active'...")
    
    success_count = 0
    for warning in warnings_to_insert:
        try:
            # We use 'upsert' to avoid duplicate errors on subsequent runs
            response = supabase.table("navarea_one_active").upsert({
                "warning_id": warning["warning_id"],
                "title": warning["title"],
                "issued_text": warning["issued_text"],
                "coordinates": warning["coordinates"],
                "cancellation_text": warning["cancellation_text"],
                "raw_text": warning["raw_text"]
            }, on_conflict="warning_id").execute()
            
            success_count += 1
            print(f"Successfully synced warning: {warning['warning_id']}")
        except Exception as e:
            print(f"Failed to sync warning {warning['warning_id']}: {e}")
            
    print(f"Finished sync operation. Successfully upserted {success_count}/{len(warnings_to_insert)} warnings.")

if __name__ == "__main__":
    sync_to_supabase()
