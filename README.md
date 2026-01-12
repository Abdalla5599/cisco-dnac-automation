# cisco-dnac-automation
DNAC / Cisco Catalyst center Automation scripts demonstrated in the training videos
# dnac-provisioning-automation
This repo contains code to provision devices from scratch

```mermaid
graph TD
    %% Styling
    classDef process fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef startEnd fill:#f9f,stroke:#333,stroke-width:2px;
    classDef loopBlock fill:#fff3e0,stroke:#ff9800,stroke-width:2px,stroke-dasharray: 5 5;

    %% Nodes
    Start((Start)):::startEnd
    
    subgraph Initialization
        LoadData[<b>load_sites_data</b><br>Read YAML File]:::process
        GetToken[<b>get_auth_token</b><br>Get API Token from DNAC]:::process
    end

    subgraph SiteLoop [Loop: For Each Site]
        CreateArea[<b>create_area</b><br>Provision Area via API]:::process
        
        subgraph BuildingLoop [Loop: For Each Building]
            CreateBuilding[<b>create_building</b><br>Provision Building via API]:::process
        end
    end

    End((End)):::startEnd

    %% Flow Connections
    Start --> LoadData
    LoadData --> GetToken
    GetToken --> CreateArea
    
    %% Loop Logic
    CreateArea --> CreateBuilding
    CreateBuilding -->|Next Building| CreateBuilding
    CreateBuilding -->|Next Site| CreateArea
    
    %% Termination
    CreateArea --> End


## Credential Provisioning Flow

The diagram below illustrates the process of preparing network credentials (CLI & SNMP) and mapping them to a specific site in Cisco Catalyst Center.

```mermaid
graph TD
    %% Styling
    classDef process fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef action fill:#d4edda,stroke:#28a745,stroke-width:2px;
    classDef startEnd fill:#f9f,stroke:#333,stroke-width:2px;

    %% Nodes
    Start((Start)):::startEnd
    
    subgraph Setup [Initialization]
        GetToken[<b>get_auth_token</b><br>Authenticate API]:::process
        GetSite[<b>get_site_id</b><br>Find Target Site ID]:::process
    end

    subgraph CLILogic [CLI Credential Handling]
        CheckCLI[<b>get_cli_credential_id</b><br>Check if User exists]:::process
        CreateCLI[<b>create_cli_credential</b><br>Create new CLI User]:::action
    end

    subgraph SNMPLogic [SNMP Credential Handling]
        CheckSNMP[<b>get_snmp_credential_id</b><br>Check if SNMP exists]:::process
        CreateSNMP[<b>create_snmp_credential</b><br>Create new SNMP string]:::action
    end

    Assign[<b>assign_credentials_to_site</b><br>Map CLI & SNMP IDs to Site]:::process
    End((End)):::startEnd

    %% Flow Connections
    Start --> GetToken
    GetToken --> GetSite
    GetSite --> CheckCLI

    %% CLI Logic Flow
    CheckCLI -->|Found| CheckSNMP
    CheckCLI -.->|Not Found| CreateCLI
    CreateCLI --> CheckSNMP

    %% SNMP Logic Flow
    CheckSNMP -->|Found| Assign
    CheckSNMP -.->|Not Found| CreateSNMP
    CreateSNMP --> Assign

    %% Final
    Assign --> End



## Discovery & Site Assignment Flow

The diagram below outlines the automation workflow for discovering network devices by IP range and immediately assigning them to a target site in Cisco Catalyst Center.

```mermaid
graph TD
    %% Styling
    classDef process fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef action fill:#d4edda,stroke:#28a745,stroke-width:2px;
    classDef wait fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef startEnd fill:#f9f,stroke:#333,stroke-width:2px;

    %% Nodes
    Start((Start)):::startEnd
    
    subgraph Init [Initialization]
        GetToken[<b>get_auth_token</b><br>Authenticate API]:::process
    end

    subgraph DiscPhase [Discovery Phase]
        StartDisc[<b>run_discovery</b><br>Initiate Discovery Job]:::action
        WaitTask[<b>wait_for_task</b><br>Poll until Job Completes]:::wait
        GetDevices[<b>get_devices_from_discovery</b><br>Fetch List of Found Devices]:::process
    end

    subgraph AssignPhase [Assignment Phase]
        ExtractIPs[Extract Management IPs]:::process
        AssignSite[<b>assign_devices_to_site</b><br>Assign IPs to Target Site]:::action
    end

    End((End)):::startEnd

    %% Flow Connections
    Start --> GetToken
    GetToken --> StartDisc
    StartDisc --> WaitTask
    WaitTask --> GetDevices
    GetDevices --> ExtractIPs
    ExtractIPs --> AssignSite
    AssignSite --> End