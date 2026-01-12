import requests
import urllib3
import time
import json
from config import DNAC_URL, USERNAME, PASSWORD, DISCOVERY_IP_RANGE, TARGET_SITE, CLI_CRED_ID, SNMP_CRED_ID, SITE_ID

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_auth_token():
    """Authenticates and returns the token."""
    url = f"{DNAC_URL}/dna/system/api/v1/auth/token"
    resp = requests.post(url, auth=(USERNAME, PASSWORD), verify=False)
    resp.raise_for_status()
    return resp.json()["Token"]

def run_discovery(token, cli_id, snmp_id):
    """Runs the discovery and returns the Task ID and Discovery ID."""
    url = f"{DNAC_URL}/dna/intent/api/v1/discovery"
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    
    job_name = f"Python_Auto_{int(time.time())}"
    
    payload = {
        "name": job_name,
        "discoveryType": "RANGE",
        "ipAddressList": DISCOVERY_IP_RANGE, 
        "protocolOrder": "ssh",
        "globalCredentialIdList": [cli_id, snmp_id]
    }
    
    print(f"[-] Starting Discovery '{job_name}' on range {DISCOVERY_IP_RANGE}...")
    resp = requests.post(url, headers=headers, json=payload, verify=False)
    
    if resp.status_code == 202:
        response_json = resp.json()['response']
        task_id = response_json['taskId']
        print(f"    [SUCCESS] Job Started! Task ID: {task_id}")
        return task_id
    else:
        print(f"    [FAIL] Error: {resp.text}")
        return None

def wait_for_task(token, task_id, timeout=300):
    """Waits for a DNAC task to complete."""
    url = f"{DNAC_URL}/dna/intent/api/v1/task/{task_id}"
    headers = {"X-Auth-Token": token}
    
    start_time = time.time()
    print(f"[-] Waiting for task {task_id} to complete...", end="", flush=True)
    
    while time.time() - start_time < timeout:
        resp = requests.get(url, headers=headers, verify=False)
        task_data = resp.json().get('response', {})
        
        if "endTime" in task_data: # Task is finished
            print(" DONE")
            return task_data
            
        print(".", end="", flush=True)
        time.sleep(5)
        
    print(" TIMEOUT")
    return None

def get_devices_from_discovery(token, discovery_id):
    """Fetches the list of devices found by a specific discovery job."""
    url = f"{DNAC_URL}/dna/intent/api/v1/discovery/{discovery_id}/network-device"
    headers = {"X-Auth-Token": token}
    
    resp = requests.get(url, headers=headers, verify=False)
    print("[-] Fetching devices from discovery...")
    # print(resp.text)
    if resp.status_code == 200:
        return resp.json().get('response', [])
    return []

def assign_devices_to_site(token, site_id, device_ips):
    """Assigns a list of device IPs to a specific Site ID."""
    # Using the Intent API to assign devices by IP
    url = f"{DNAC_URL}/dna/intent/api/v1/assign-device-to-site/{site_id}/device"
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    
    # Payload structure requires a list of dicts: {"ip": "x.x.x.x"}
    payload = {"device": [{"ip": ip} for ip in device_ips]}
    
    print(f"[-] Assigning {len(device_ips)} device(s) to site ID {site_id}...")
    resp = requests.post(url, headers=headers, json=payload, verify=False)
    print(resp.text)
    
    if resp.status_code == 202:
        print("    [SUCCESS] Assignment task submitted successfully.")
        task_id = resp.json()['executionId']
        # wait_for_task(token, task_id) # Optional: Wait for assignment to finish
    else:
        print(f"    [FAIL] Assignment failed: {resp.text}")
        
        
if __name__ == "__main__":
    
    token = get_auth_token()
    
    cli = CLI_CRED_ID
    snmp =SNMP_CRED_ID
    site_id = SITE_ID
    
    if cli and snmp and site_id:
        # 3. Run Discovery
        task_id = run_discovery(token, cli, snmp)
        print(f"Task ID: {task_id}")  
        
        if task_id:
            # 4. Wait for Discovery to Complete
            task_result = wait_for_task(token, task_id)
            
            if task_result and not task_result.get("isError"):
                # 5. Get the Discovered Devices (IPs)
                # We query the specific discovery job to see what it found
                print("Task Result:")
                print(task_result)
                
                discovery_id = json.loads(task_result['data'])['discoveryId']
                print(f"Discovery ID: {discovery_id}")
                discovered_devices = get_devices_from_discovery(token, discovery_id)
                print('Discovered Devices:')
                print(discovered_devices)  
                
                target_ips = [d['managementIpAddress'] for d in discovered_devices] 

                if target_ips:
                    print(f"[-] Discovery found {len(target_ips)} device(s): {target_ips}")
                    
                    # 6. Assign to Site (This handles moving them if they are in another site)
                    assign_devices_to_site(token, site_id, target_ips)
                else:
                    print("[!] No devices found in this discovery run.")              
            else:
                print("[!] Discovery Task failed or timed out.")   