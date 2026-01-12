import requests
import urllib3
import json
import time
from config import DNAC_URL, USERNAME, PASSWORD, TARGET_SITE, NEW_CLI_USER, NEW_CLI_PASS, SNMP_RO_COMMUNITY, SNMP_DESCRIPTION

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

### 01
def get_auth_token():
    """Authenticates with DNAC and returns the token."""
    url = f"{DNAC_URL}/dna/system/api/v1/auth/token"
    resp = requests.post(url, auth=(USERNAME, PASSWORD), verify=False)
    resp.raise_for_status()
    return resp.json()["Token"]

### 02 Get Site_ID
def get_site_id(token, site_name_hierarchy):
    """Finds the Site ID based on the hierarchy name."""
    url = f"{DNAC_URL}/dna/intent/api/v1/site"
    headers = {"X-Auth-Token": token}
    
    resp = requests.get(url, headers=headers, verify=False)
    if resp.status_code == 200:
        sites = resp.json().get('response', [])
        # print(sites)
        for site in sites:
            if site['siteNameHierarchy'] == site_name_hierarchy:
                return site['id']
    print(f"[!] Site '{site_name_hierarchy}' not found.")
    return None

def get_cli_credential_id(token, username):
    """Fetches the ID of an existing CLI credential by username."""
    url = f"{DNAC_URL}/dna/intent/api/v1/global-credential?credentialSubType=CLI"
    headers = {"X-Auth-Token": token}
    
    resp = requests.get(url, headers=headers, verify=False)
    if resp.status_code == 200:
        creds = resp.json().get('response', [])
        print(creds)
        for cred in creds:
            if cred['username'] == username:
                return cred['id']
    return None

def create_cli_credential(token, cred_username, cred_password, description="Python Created CLI"):
    """Creates a Global CLI Credential."""
    url = f"{DNAC_URL}/dna/intent/api/v1/global-credential/cli"
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    
    payload = [{
        "username": cred_username,
        "password": cred_password,
        "description": description,
        "comments": "Created via Python Script"
    }]
    
    print(f"[-] Creating Global CLI Credential for user '{cred_username}'...")
    resp = requests.post(url, headers=headers, json=payload, verify=False)
    
    if resp.status_code == 202:
        print(f"    [SUCCESS] CLI creation task started.")
        time.sleep(3) # Wait for backend consistency
        return get_cli_credential_id(token, cred_username)
    else:
        print(f"    [FAIL] Failed to create CLI credential: {resp.text}")
        return None

def get_snmp_credential_id(token, description):
    """
    Fetches the ID of an existing SNMP credential.
    Note: We filter by Description because community strings are not unique keys.
    """
    url = f"{DNAC_URL}/dna/intent/api/v1/global-credential?credentialSubType=SNMPV2_READ_COMMUNITY"
    headers = {"X-Auth-Token": token}
    
    resp = requests.get(url, headers=headers, verify=False)
    if resp.status_code == 200:
        creds = resp.json().get('response', [])
        for cred in creds:
            # We match on description as the unique identifier for our script logic
            if cred.get('description') == description:
                return cred['id']
    return None

def create_snmp_credential(token, read_community, description):
    """Creates a Global SNMPv2 Read Credential."""
    url = f"{DNAC_URL}/dna/intent/api/v1/global-credential/snmpv2-read-community"
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    
    payload = [{
        "description": description,
        "comments": "Created via Python Script",
        "readCommunity": read_community
    }]
    
    print(f"[-] Creating SNMPv2 Credential '{description}'...")
    resp = requests.post(url, headers=headers, json=payload, verify=False)
    
    if resp.status_code == 202:
        print(f"    [SUCCESS] SNMP creation task started.")
        time.sleep(3) # Wait for backend consistency
        return get_snmp_credential_id(token, description)
    else:
        print(f"    [FAIL] Failed to create SNMP credential: {resp.text}")
        return None

def assign_credentials_to_site(token, site_id, cli_id=None, snmp_id=None):
    """Assigns CLI and/or SNMP credentials to the specific Site."""
    url = f"{DNAC_URL}/dna/intent/api/v1/credential-to-site/{site_id}"
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    
    payload = {}
    if cli_id:
        payload["cliId"] = cli_id
    if snmp_id:
        payload["snmpV2ReadId"] = snmp_id
    
    if not payload:
        print("[!] No IDs provided to assign.")
        return

    print(f"[-] Assigning Credentials to Site ID '{site_id}'...")
    print(f"    [CLI_ID] {cli_id} | [SNMP_ID] {snmp_id} | [STATUS] Assignment task accepted.")
    
    resp = requests.post(url, headers=headers, json=payload, verify=False)
    
    if resp.status_code == 202:
        print(f"    [SUCCESS] Assignment task accepted.")
    else:
        print(f"    [FAIL] Assignment failed: {resp.text}")
        

if __name__ == "__main__":
    try:
        token = get_auth_token()
        # print(token)
        print("[+] Authentication Successful")
    except Exception as e:
        print(f"[!] Authentication Failed: {e}")
        
    ## get site ID
    site_id = get_site_id(token, TARGET_SITE)
    print(site_id)

    if site_id:
    #### Handle CLI Cred
        # 2a. Handle CLI Credential
        cli_id = get_cli_credential_id(token, NEW_CLI_USER)
        if not cli_id:
            cli_id = create_cli_credential(token, NEW_CLI_USER, NEW_CLI_PASS)
        else:
            print(f"[-] CLI Credential '{NEW_CLI_USER}' already exists. ID: {cli_id}")

    ##### Handle SNMP Creds
        snmp_id = get_snmp_credential_id(token, SNMP_DESCRIPTION)
        if not snmp_id:
            snmp_id = create_snmp_credential(token, SNMP_RO_COMMUNITY, SNMP_DESCRIPTION)
        else:
            print(f"[-] SNMP Credential '{SNMP_DESCRIPTION}' already exists. ID: {snmp_id}")
         
        # 3. Assign Both to Site
        if cli_id or snmp_id:
            assign_credentials_to_site(token, site_id, cli_id, snmp_id)
        else:
            print("[!] Could not retrieve valid Credential IDs.")
    else:
        print("[!] Stopping script as Site ID was not found.")