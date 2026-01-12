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