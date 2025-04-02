import requests
import json
import pandas as pd
import xmltodict
from packageurl import PackageURL

# GitLab Configuration
GITLAB_URL = "https://gitlab.com"  # Change if using self-hosted GitLab
PRIVATE_TOKEN = "your_private_token"  # Replace with your GitLab API token

# Headers for API Authentication
HEADERS = {"Private-Token": PRIVATE_TOKEN}

# List of package files to check
PACKAGE_FILES = ["requirements.txt", "package.json", "pom.xml"]

def get_all_projects():
    """Fetches all repositories from GitLab."""
    projects = []
    url = f"{GITLAB_URL}/api/v4/projects?per_page=100"
    
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print("❌ Error fetching projects:", response.text)
            return []
        
        projects.extend(response.json())
        url = response.links.get("next", {}).get("url")  # Pagination
    
    return projects

def get_file_content(project_id, file_path):
    """Fetches the raw content of a file from a GitLab repository."""
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/files/{file_path}/raw?ref=main"
    response = requests.get(url, headers=HEADERS)
    
    return response.text if response.status_code == 200 else None

def extract_dependencies(project):
    """Searches for dependency files and extracts library data."""
    dependencies = []
    
    for file_path in PACKAGE_FILES:
        content = get_file_content(project["id"], file_path)
        if content:
            if file_path == "requirements.txt":
                dependencies.extend(parse_requirements_txt(content))
            elif file_path == "package.json":
                dependencies.extend(parse_package_json(content))
            elif file_path == "pom.xml":
                dependencies.extend(parse_pom_xml(content))
    
    return dependencies

def parse_requirements_txt(content):
    """Parses a Python requirements.txt file."""
    dependencies = []
    for line in content.split("\n"):
        if line and not line.startswith("#"):
            parts = line.split("==")
            package = parts[0].strip()
            version = parts[1].strip() if len(parts) > 1 else "unknown"
            dependencies.append(format_dependency(package, version, "pypi"))
    return dependencies

def parse_package_json(content):
    """Parses a Node.js package.json file."""
    dependencies = []
    try:
        data = json.loads(content)
        for dep, version in data.get("dependencies", {}).items():
            dependencies.append(format_dependency(dep, version, "npm"))
        for dep, version in data.get("devDependencies", {}).items():
            dependencies.append(format_dependency(dep, version, "npm"))
    except json.JSONDecodeError:
        pass
    return dependencies

def parse_pom_xml(content):
    """Parses a Java Maven pom.xml file."""
    dependencies = []
    try:
        data = xmltodict.parse(content)
        deps = data.get("project", {}).get("dependencies", {}).get("dependency", [])
        if isinstance(deps, dict):  # Convert single dependency to list
            deps = [deps]
        for dep in deps:
            group_id = dep.get("groupId", "").strip()
            artifact_id = dep.get("artifactId", "").strip()
            version = dep.get("version", "unknown").strip()
            dependencies.append(format_dependency(f"{group_id}:{artifact_id}", version, "maven"))
    except Exception:
        pass
    return dependencies

def format_dependency(library, version, package_type):
    """
    Formats dependencies into Package URL (purl) and Common Platform Enumeration (CPE).
    
    Args:
        library (str): Library name
        version (str): Library version
        package_type (str): Package ecosystem ("pypi", "npm", "maven")

    Returns:
        dict: Formatted dependency data
    """
    purl = PackageURL(type=package_type, name=library, version=version).to_string()
    cpe = f"cpe:2.3:a:{library}:{library}:{version}:*:*:*:*:*:*:*"
    
    return {
        "library": library,
        "version": version,
        "type": package_type,
        "purl": purl,
        "cpe": cpe
    }

def save_to_json(results, filename="gitlab_libraries.json"):
    """Saves results to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"✅ JSON saved to {filename}")

def save_to_csv(results, filename="gitlab_libraries.csv"):
    """Saves results to a CSV file."""
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"✅ CSV saved to {filename}")

def main():
    """Fetches all repositories, extracts dependencies, and saves the results."""
    projects = get_all_projects()
    if not projects:
        print("No projects found.")
        return

    print(f"🔍 Extracting dependencies from {len(projects)} repositories...")

    result = []
    for project in projects:
        dependencies = extract_dependencies(project)
        for dep in dependencies:
            result.append({
                "project": project["name"],
                "project_url": project["web_url"],
                "library": dep["library"],
                "version": dep["version"],
                "type": dep["type"],
                "purl": dep["purl"],
                "cpe": dep["cpe"]
            })

    if result:
        save_to_json(result)
        save_to_csv(result)
    else:
        print("❌ No dependencies found.")

if __name__ == "__main__":
    main()
