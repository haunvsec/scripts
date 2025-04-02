import requests
import json
import csv
import pandas as pd

# GitLab Configuration
GITLAB_URL = "https://gitlab.com"  # Change if using a self-hosted GitLab instance
PRIVATE_TOKEN = "your_private_token"  # Replace with your GitLab API token
SEARCH_KEYWORD = "password"  # Change to the keyword you want to search

# Set API Headers
HEADERS = {"Private-Token": PRIVATE_TOKEN}

# Function to fetch all projects from GitLab
def get_all_projects():
    """
    Fetches all repositories (projects) from the GitLab instance.

    Returns:
        List of project dictionaries.
    """
    projects = []
    url = f"{GITLAB_URL}/api/v4/projects?per_page=100"
    
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print("❌ Error fetching project list:", response.text)
            return []
        
        projects.extend(response.json())
        url = response.links.get("next", {}).get("url")  # Check if there's a next page
    
    return projects

# Function to search for a keyword in a specific GitLab project
def search_in_project(project_id):
    """
    Searches for a keyword within a given GitLab project.

    Args:
        project_id (int): The ID of the GitLab project.

    Returns:
        List of search results containing file paths and matching lines.
    """
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/search?scope=blobs&search={SEARCH_KEYWORD}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"❌ Error searching in project {project_id}: {response.text}")
        return []
    
    return response.json()

# Function to save results to JSON
def save_to_json(results, filename="gitlab_search_results.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"✅ Results saved to {filename}")

# Function to save results to CSV
def save_to_csv(results, filename="gitlab_search_results.csv"):
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"✅ Results saved to {filename}")

# Main function to execute the search
def main():
    """
    Fetches all repositories, searches for the specified keyword, 
    and saves the results in JSON and CSV formats.
    """
    projects = get_all_projects()
    if not projects:
        print("No projects found.")
        return

    print(f"🔍 Searching for keyword '{SEARCH_KEYWORD}' in {len(projects)} repositories...")

    result = []
    for project in projects:
        search_results = search_in_project(project["id"])
        for item in search_results:
            result.append({
                "project": project["name"],
                "file": item["path"],
                "line": item.get("data", "").strip()
            })
    
    if result:
        save_to_json(result)
        save_to_csv(result)
    else:
        print("❌ No results found.")

if __name__ == "__main__":
    main()
