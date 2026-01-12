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