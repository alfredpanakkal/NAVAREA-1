import re
import json
import hashlib
from datetime import datetime, timezone

def convert_to_decimal(degrees, minutes, direction):
    decimal = float(degrees) + (float(minutes) / 60.0)
    if direction in ['S', 'W']:
        decimal = -decimal
    return round(decimal, 6)

def parse_coordinates(raw_text):
    # Regex for 52-07.7N 003-56.4E
    pattern = r'(\d{2,3})-(\d{2}\.\d)[N|S]\s+(\d{3})-(\d{2}\.\d)[E|W]'
    matches = re.finditer(pattern, raw_text)
    
    parsed_coords = []
    points = []
    
    for match in matches:
        lat_deg, lat_min = match.group(1), match.group(2)
        lat_dir = raw_text[match.end(2)]
        
        lon_deg, lon_min = match.group(3), match.group(4)
        lon_dir = raw_text[match.end(4)]
        
        lat = convert_to_decimal(lat_deg, lat_min, lat_dir)
        lon = convert_to_decimal(lon_deg, lon_min, lon_dir)
        
        points.append([lon, lat]) # GeoJSON uses [lon, lat]
        parsed_coords.append(f"{lat_deg}-{lat_min}{lat_dir} {lon_deg}-{lon_min}{lon_dir}")
        
    spatial = None
    primary_lat = None
    primary_lon = None
    
    if points:
        primary_lat = points[0][1]
        primary_lon = points[0][0]
        if len(points) == 1:
            spatial = {"type": "Point", "coordinates": points[0]}
        elif len(points) > 1:
            spatial = {"type": "LineString", "coordinates": points}
            
    return parsed_coords, primary_lat, primary_lon, spatial

def classify_hazard(raw_text):
    text = raw_text.upper()
    if any(keyword in text for keyword in ["LIGHT", "BUOY", "RACON", "BEACON"]):
        return "aton"
    elif any(keyword in text for keyword in ["FIRING", "GUNNERY", "MISSILE", "WEAPON"]):
        return "military"
    elif any(keyword in text for keyword in ["SEISMIC", "CABLE", "PIPELINE", "ROV", "TOWING"]):
        return "subsea"
    elif any(keyword in text for keyword in ["DRIFTING", "DERELICT", "MINE"]):
        return "drifting"
    elif any(keyword in text for keyword in ["RIG", "PLATFORM", "JACK-UP"]):
        return "offshore"
    return "general"

def parse_warning(raw_block, reference_header):
    warning_id = reference_header.split("NAVAREA I ")[-1].strip()
    
    lines = [line.strip() for line in raw_block.split('\n') if line.strip()]
    title = lines[0] if lines else ""
    
    coords_text, lat, lon, spatial = parse_coordinates(raw_block)
    
    date_pattern = r'(\d{6}\sUTC\s[A-Z]{3}\s\d{4})'
    date_match = re.search(date_pattern, title)
    issued_text = date_match.group(1) if date_match else None

    hazard = classify_hazard(raw_block)
    checksum = hashlib.sha256(raw_block.encode('utf-8')).hexdigest()

    raw_message = {
        "warning_id": warning_id,
        "source_id": "ukho-navarea-1",
        "subject_header": reference_header,
        "full_raw_text": raw_block,
        "received_timestamp": datetime.now(timezone.utc).isoformat(),
        "checksum_sha256": checksum
    }
    
    nav_warning = {
        "warning_id": warning_id,
        "source_id": "ukho-navarea-1",
        "navarea": "I",
        "title": title,
        "issued_text": issued_text,
        "coordinates": ", ".join(coords_text) if coords_text else None,
        "latitude": lat,
        "longitude": lon,
        "spatial": spatial,
        "category": hazard,
        "status": "active",
        "is_cancelled": False,
        "raw_text": raw_block,
        "extraction_method": "deterministic"
    }
    
    return raw_message, nav_warning

def main():
    try:
        with open("navarea_1_warnings.txt", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: navarea_1_warnings.txt not found.")
        return

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
        
    print(f"Successfully parsed {len(matches)} warnings into parsed_warnings.json with WGS84 coords and semantic tags.")

if __name__ == "__main__":
    main()
