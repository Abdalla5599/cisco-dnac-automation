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