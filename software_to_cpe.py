import csv
import json

def sanitize(value):
    """
    Normalize a string for CPE format:
    - Convert to lowercase
    - Replace spaces with underscores
    """
    return value.lower().replace(" ", "_")

def build_cpe(vendor, product, version):
    """
    Construct a CPE identifier from vendor, product, and version.
    Format: cpe:2.3:a:<vendor>:<product>:<version>:*:*:*:*:*:*:*
    """
    cpe = f"cpe:2.3:a:{sanitize(vendor)}:{sanitize(product)}:{version}:*:*:*:*:*:*:*"
    return cpe

def process_nexpose_csv(input_file, output_file_json, output_file_csv):
    """
    Process a CSV file from Nexpose scan results, generate CPE identifiers,
    and export the results to both JSON and CSV formats.
    
    :param input_file: Path to input CSV file from Nexpose
    :param output_file_json: Path to output JSON file
    :param output_file_csv: Path to output CSV file
    """
    results = []
    
    with open(input_file, encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            vendor = row.get("Vendor", "unknown")  # Default to 'unknown' if missing
            product = row.get("Software", "unknown")
            version = row.get("Version", "unknown")
            
            cpe = build_cpe(vendor, product, version)
            results.append({"vendor": vendor, "product": product, "version": version, "cpe": cpe})

    # Export data to JSON format
    with open(output_file_json, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4)
    
    # Export data to CSV format
    with open(output_file_csv, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["vendor", "product", "version", "cpe"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✅ CPE Data saved: {output_file_json}, {output_file_csv}")

# Run the script with specified file paths
input_csv = "nexpose_data.csv"  # Input file from Nexpose scan
output_json = "cpe_data.json"    # Output JSON file
output_csv = "cpe_data.csv"      # Output CSV file

process_nexpose_csv(input_csv, output_json, output_csv)
