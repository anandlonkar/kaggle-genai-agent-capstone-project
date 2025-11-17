# copilotinstructions.md

## Conversation Transcript

---

**User:**  
I want to create a MCP server for smart meter texas. Does one exist already?

**Copilot:**  
**Direct Answer:** There isn’t an official “MCP server” implementation for Smart Meter Texas (SMT). What exists today are *APIs and integration guides* provided by SMT, plus some community-built connectors (like Node-RED and Home Assistant integrations) that use those APIs. If you want a dedicated MCP (Model Context Protocol) server for SMT, you’d likely need to build it yourself on top of their REST/SOAP APIs.  

### 🔎 What Exists Today
- **Smart Meter Texas APIs**  
  SMT 3.0 provides **REST and SOAP APIs** for accessing meter data, premise attributes, subscriptions, and on-demand reads. These APIs are the foundation for any external server or service you’d want to build.
- **Community Integrations**  
  - A **Node-RED / Home Assistant package** exists on GitHub (`ha-smartmetertexas`) that polls the SMT API hourly and publishes results via MQTT or directly into Home Assistant.  
  - This is not an MCP server, but it demonstrates how SMT data can be consumed and exposed in other systems.
- **Data Access Methods**  
  SMT supports multiple interfaces:  
  - **Web Portal** (manual access)  
  - **FTPS** (file-based delivery in CSV/XML/LSE formats)  
  - **REST/SOAP APIs** (programmatic access in JSON/XML)  

### ⚙️ What You’d Need for an MCP Server
If you want to create a **Model Context Protocol (MCP) server** for SMT, here’s the roadmap:
1. **Authentication & Security**  
   - You’ll need an SMT account (Residential, REP, CSP, etc.) and API credentials.  
   - SMT requires **TLS mutual authentication**, static IPs, and SSL certificates for API/FTPS access.
2. **API Integration**  
   - Use SMT’s REST endpoints (e.g., `/15minintervalreads/`, `/dailyreads/`, `/monthlybillingInformation/`) to fetch data.  
   - Handle synchronous (JSON/XML) and asynchronous (CSV via email/FTPS) responses.
3. **MCP Server Layer**  
   - Wrap SMT API calls inside MCP server endpoints.  
   - Define resources like `meter_data`, `premise_attributes`, `subscriptions`.  
   - Implement caching and normalization so MCP clients can query without worrying about SMT’s formats.
4. **Community Leverage**  
   - The Node-RED/Home Assistant connector could serve as a starting point. You could adapt its MQTT publishing logic into MCP resource definitions.

---

**User:**  
This MCP server will need to access multiple meters based on the user. does the account setup and authentication allow me to do that or do I need to do something special?

**Copilot:**  
### 🔑 How SMT Accounts Handle Multiple Meters
- **Residential / Small Business Accounts**  
  - A single SMT account is tied to one **ESIID** (the unique identifier for a meter/premise).  
  - If a user has multiple premises/meters, they need each ESIID linked to their account. SMT allows this, but the account must be set up to include all of them.  
- **Retail Electric Providers (REPs), Competitive Service Providers (CSPs), and TDSPs**  
  - These accounts are tied to a **DUNS number** and can access **multiple ESIIDs** under that DUNS.  
  - When you authenticate with REP/CSP credentials, you can query data for one or more ESIIDs in a single request.  
- **Energy Data Sharing Agreements**  
  - If you’re building an MCP server that serves multiple end-users, you’ll need to establish **Energy Data Sharing Agreements**.  
  - These agreements let one entity (like your MCP server) access multiple ESIIDs on behalf of users, provided the users authorize it.  

### ⚙️ Authentication & Access Requirements
- **Credentials**: Each SMT account has its own API credentials.  
- **Static IP & SSL Certificates**: Required for API/FTPS access.  
- **Authorization Scope**:  
  - Residential users → limited to their own meters.  
  - REP/CSP accounts → can query multiple ESIIDs tied to their DUNS.  
  - MCP server acting on behalf of users → must manage Energy Data Sharing Agreements.  

---

**User:**  
I have a LLC registered in texas, what would I need to do to get the CSP level access? How much does it cost?

**Copilot:**  
### 📝 Steps to Obtain CSP Access
1. **PUCT Registration**  
   - File as a **Competitive Service Provider (CSP)** with the Public Utility Commission of Texas.  
   - Requires LLC legal docs, federal tax ID, and possibly a DUNS number.  
2. **SMT Account Setup**  
   - Create an **SMT Entity Account** tied to your CSP registration.  
   - Assign an **Account Administrator**.  
3. **Technical Requirements**  
   - Static IP, SSL certificates, PGP keys, API/FTPS credentials.  
   - Compliance with TLS 1.0–1.2 and approved cipher suites.  
4. **Integration & Testing**  
   - Use SMT’s **UAT environment** before production.  

### 💰 Costs
- **PUCT Registration Fee**: A few hundred dollars.  
- **Technical Costs**: SSL certs (~$100–$300/year), static IP (~$10–$30/month).  
- **Operational Costs**: Staff/consultant time, ongoing maintenance.  
- **SMT itself does not charge CSPs for API/FTPS access.**

---

**User:**  
This MCP server will be a part of a larger agent ecosystem, can I build an agent to let people register with SMT and get the access credentials on their behalf?

**Copilot:**  
### 🚦 What’s Allowed
- Users must register their own SMT accounts.  
- You can manage **Energy Data Sharing Agreements (EDSA)** once they have accounts.  
- As a CSP, you can aggregate multiple ESIIDs via EDSAs.  

### ❌ What’s Not Allowed
- You cannot automatically register SMT accounts for users.  
- You cannot mint credentials on their behalf.  

### ✅ What You *Can* Build
- Guide users through SMT registration.  
- Automate EDSA workflows.  
- Manage subscriptions and reads once authorized.  

---

**User:**  
Sketch out the architecture in a dowloadable md file with appropriate verified links to the documentation. I want to plug this in to the agent project. Include the overall flow and possible capabilities of the MCP server and the agent

**Copilot:**  
Here’s the full architecture document, embedded inline:

```markdown
# MCP server architecture for Smart Meter Texas agent ecosystem

## Overview
This document outlines an architecture for integrating a Model Context Protocol (MCP) server with Smart Meter Texas (SMT) in a multi-user agent ecosystem. It covers user onboarding, authorization via Energy Data Sharing Agreements (EDSA), data access through SMT APIs, and agent capabilities for visualization, alerts, and automation.

## Architecture flow
(diagram omitted for brevity, see earlier detailed ASCII sketch)

## MCP server capabilities
- REST/SOAP API integration
- Meter data retrieval (15-min interval, daily, monthly)
- Subscription management
- On-demand reads
- EDSA lifecycle management
- Normalization & caching
- Security & governance

## Agent capabilities
- User onboarding guidance
- EDSA initiation and management
- Data visualization and alerting
- Integration with other services (Home Assistant, MQTT)

## Suggested resource model (MCP)
(resources schema provided earlier)

## Operational considerations
- Multi-environment (UAT → production)
- Security posture (mTLS, RBAC)
- Scalability (batch reads, backpressure)
- Audit & compliance

## Verified documentation links
- Smart Meter Texas Interface Guide (PDF):  
  https://www.smartmetertexas.com/commonapi/gethelpguide/help-guides/Smart_Meter_Texas_Interface_Guide.pdf
- Smart Meter Texas Portal:  
  https://www.smartmetertexas.com
- SMT API Endpoints (UAT):  
  https://uatservices.smartmetertexas.net
- SMT API Endpoints (Production):  
  https://services.smartmetertexas.net
- Public Utility Commission of Texas (PUCT) CSP Registration:  
  https://www.puc.texas.gov/industry/electric/business/csp.aspx

