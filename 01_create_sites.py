import requests
import urllib3
import yaml
import time
from config import DNAC_URL, USERNAME, PASSWORD

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_auth_token():
    """Authenticates with DNAC and returns the token."""
    url = f"{DNAC_URL}/dna/system/api/v1/auth/token"
    resp = requests.post(url, auth=(USERNAME, PASSWORD), verify=False)
    resp.raise_for_status()
    return resp.json()["Token"]

def load_sites_data(filename="sites.yml"):
    """Reads the YAML file and returns the data."""
    with open(filename, 'r') as file:
        return yaml.safe_load(file)


def create_area(token, area_name, parent_name="Global"):
    """Creates a Site (Area) in DNAC."""
    url = f"{DNAC_URL}/dna/intent/api/v1/site"
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    
    payload = {
        "type": "area",
        "site": {
            "area": {
                "name": area_name,
                "parentName": parent_name
            }
        }
    }
    
    print(f"[-] Creating Area '{area_name}' under '{parent_name}'...")
    try:
        resp = requests.post(url, headers=headers, json=payload, verify=False)
        if resp.status_code == 202:
            print(f"    [SUCCESS] Server accepted request for Area: {area_name}")
            return True
        else:
            print(f"    [FAIL] Status {resp.status_code}: {resp.json()}")
            return False
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False
    
def create_building(token, building_data, parent_path):
    """Creates a Building under a specific Area hierarchy."""
    url = f"{DNAC_URL}/dna/intent/api/v1/site"
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    
    building_name = building_data['name']
    
    payload = {
        "type": "building",
        "site": {
            "building": {
                "name": building_name,
                "parentName": parent_path,
                "address": building_data['address'],
                "latitude": building_data['latitude'],
                "longitude": building_data['longitude']
            }
        }
    }

    print(f"    [-] Creating Building '{building_name}' under '{parent_path}'...")
    try:
        resp = requests.post(url, headers=headers, json=payload, verify=False)
        if resp.status_code == 202:
            print(f"        [SUCCESS] Server accepted request for Building: {building_name}")
        else:
            print(f"        [FAIL] Status {resp.status_code}: {resp.json()}")
    except Exception as e:
        print(f"        [ERROR] {e}")
        
        
if __name__ == "__main__":
    try:
        token = get_auth_token()
        # print(token)
        print("[+] Authentication Successful")
    except Exception as e:
        print(f"[!] Authentication Failed: {e}")    
    
    data = load_sites_data()  
    # print(data)
    if "sites" in data:
        for site in data["sites"]:
            site_name = site["name"]
            parent_name = site.get("parentName", "Global") 
            
            create_area(token, site_name, parent_name)
            area_hierarchy = f"{parent_name}/{site_name}"


            if "buildings" in site:
                for building in site["buildings"]:
                    create_building(token, building, area_hierarchy)           
            else:
                print(f"    [INFO] No buildings defined for {site_name}")
                
            print("-" * 40)
                    
    
    else:
        print("[!] No 'sites' key found in YAML file.")
