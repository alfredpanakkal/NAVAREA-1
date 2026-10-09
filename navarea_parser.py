import re
import json
from datetime import datetime, timezone

def parse_warning(raw_block, reference_header):
    # warning_id extraction: "NAVAREA I 223/26" -> "223/26"
    warning_id = reference_header.split("NAVAREA I ")[-1].strip()
    
    # Title extraction: The first non-empty line of the block
    lines = [line.strip() for line in raw_block.split('\n') if line.strip()]
    title = lines[0] if lines else ""
    
    # Coordinate extraction
    coord_pattern = r'\d{2}-\d{2}\.\d[NS]\s+\d{3}-\d{2}\.\d[EW]'
    coordinates = re.findall(coord_pattern, raw_block)
    
    # Cancellation text extraction
    cancel_pattern = r'(CANCEL NAVAREA I \d+/\d+\.?)'
    cancellation_match = re.search(cancel_pattern, raw_block)
    cancellation_text = cancellation_match.group(1) if cancellation_match else None
    
    # Issued Text (Optional Date matching in the first line)
    date_pattern = r'(\d{6}\sUTC\s[A-Z]{3}\s\d{4})'
    date_match = re.search(date_pattern, title)
    issued_text = date_match.group(1) if date_match else None

    # Construct the data objects corresponding to the DB schema
    raw_message = {
        "warning_id": warning_id,
        "source_id": "ukho-navarea-1",
        "subject_header": reference_header,
        "full_raw_text": raw_block,
        "received_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    nav_warning = {
        "warning_id": warning_id,
        "source_id": "ukho-navarea-1",
        "navarea": "I",
        "title": title,
        "issued_text": issued_text,
        "coordinates": coordinates,
        "status": "active",
        "raw_text": raw_block,
        "cancellation_text": cancellation_text
    }
    
    return raw_message, nav_warning

def main():
    try:
        with open("navarea_1_warnings.txt", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: navarea_1_warnings.txt not found.")
        return

    # Split by the header separator "--- NAVAREA I ... ---"
    # We use regex to find all headers and the blocks between them
    pattern = r'--- (NAVAREA I \d+/\d+) ---\n(.*?)(?=\n--- NAVAREA I|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    parsed_data = {
        "raw_messages": [],
        "nav_warnings": []
    }
    
    for header, block in matches:
        raw_msg, nav_warn = parse_warning(block.strip(), header.strip())
        parsed_data["raw_messages"].append(raw_msg)
        parsed_data["nav_warnings"].append(nav_warn)
        
    with open("parsed_warnings.json", "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=4)
        
    print(f"Successfully parsed {len(matches)} warnings into parsed_warnings.json")

if __name__ == "__main__":
    main()
