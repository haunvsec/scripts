import requests
import csv
import json

# GitLab API Settings
GITLAB_URL = "https://gitlab.com"  # Change if using self-hosted GitLab
PRIVATE_TOKEN = "your_gitlab_api_token"  # Replace with your GitLab API token
SEARCH_TERM = "your_search_keyword"  # Replace with the keyword to search

# Headers for authentication
HEADERS = {"PRIVATE-TOKEN": PRIVATE_TOKEN}

def global_search():
    """Search for a keyword globally across all GitLab projects"""
    search_results = []
    page = 1
    while True:
        response = requests.get(f"{GITLAB_URL}/api/v4/search", headers=HEADERS, params={"scope": "blobs", "search": SEARCH_TERM, "page": page, "per_page": 100})
        
        if response.status_code != 200:
            print(f"Error during search: {response.text}")
            break
        
        results = response.json()
        if not results:
            break
        
        for result in results:
            search_results.append({
                "project_name": result.get("project", {}).get("name"),
                "project_url": result.get("project", {}).get("web_url"),
                "file_path": result.get("path"),
                "line_number": result.get("startline"),
                "snippet": result.get("data")
            })
        
        page += 1
    return search_results

def main():
    """Main function to perform global search and export results"""
    all_results = global_search()
    
    # Save to JSON
    with open("gitlab_global_search_results.json", "w", encoding="utf-8") as json_file:
        json.dump(all_results, json_file, indent=4)
    
    # Save to CSV
    with open("gitlab_global_search_results.csv", "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["project_name", "project_url", "file_path", "line_number", "snippet"])
        writer.writeheader()
        writer.writerows(all_results)
    
    print("✅ Global search completed. Results saved to JSON and CSV.")

if __name__ == "__main__":
    main()
