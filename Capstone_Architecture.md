# Capstone Project: AI Agent for Texas Electricity Plan Optimization

## 1. Project Vision & Goals

This document outlines the architecture for a capstone project for the "5-day Agents Intensive Course." The project's goal is to create an intelligent agent that helps Texas residents find the most cost-effective electricity plan by analyzing their personal energy consumption data from Smart Meter Texas (SMT).

The agent will manage the entire process: guiding users to authorize data access, fetching their historical usage, analyzing it against available market plans, and presenting a personalized recommendation.

### Key Objectives:
- **Simplify User Onboarding**: Abstract away the complexities of SMT registration and data sharing agreements.
- **Automate Data Analysis**: Eliminate the need for users to manually download and analyze their usage data.
- **Provide Actionable Recommendations**: Deliver a clear, data-driven recommendation for the best electricity plan.
- **Build a Scalable Agentic Ecosystem**: Create a robust system using a modern agent framework (e.g., Google's framework) that can be extended with new capabilities.

---

## 2. High-Level Architecture

The ecosystem consists of four main components: the **User**, the **Plan Advisor Agent**, the **MCP Server** (acting as the interface to Smart Meter Texas), and a **Plan Scraper/API** for fetching electricity plans.

### Architecture Diagram

This diagram shows the relationships between the components. The Agent is the central orchestrator, communicating with the user and the backend services. You can open the `Architecture.drawio.xml` file to edit the diagram.

---

## 3. User Journey & Data Flow

The following sequence diagram illustrates the end-to-end flow, from the user's first interaction to receiving a plan recommendation.

### Sequence Diagram
You can open the `Sequence.drawio.xml` file to edit the diagram.

---

## 4. Component Responsibilities

### Plan Advisor Agent
- **Framework**: Built on the Google agent framework.
- **User Interaction**: Manages the conversation, guiding the user through the necessary steps.
- **Onboarding**: Provides clear instructions for the user to sign up for a Smart Meter Texas account. It **does not** create an account on their behalf.
- **Authorization Orchestration**: Initiates the Energy Data Sharing Agreement (EDSA) process by calling the MCP server and informs the user they need to log in to SMT to approve it.
- **Data Analysis**: Once it receives usage data from the MCP server and plan data from the Plan API, it runs calculations to determine the total cost for each plan based on the user's historical consumption patterns.
- **Tool Usage**:
    - Uses the `MCP Server` as a tool to get meter data.
    - Uses the `Plan API` as a tool to get electricity plans.

### MCP Server (for Smart Meter Texas)
- **API Abstraction**: Provides a simple, clean REST/MCP-style API for the agent to consume, hiding the complexity of SMT's various interfaces (REST/SOAP/FTPS).
- **SMT Integration**: Handles the direct communication with SMT APIs. This includes managing the required mTLS authentication, static IPs, and SSL certificates.
- **EDSA Management**: Contains the logic to programmatically create, monitor, and manage Energy Data Sharing Agreements with SMT on behalf of users.
- **Data Normalization & Caching**: Fetches data in various SMT formats (JSON, XML, CSV) and normalizes it into a consistent model (e.g., a simple time-series JSON array). It should also cache this data to improve performance and respect SMT rate limits.
- **Security**: Acts as a secure proxy. The agent does not need to store or handle any SMT-specific credentials. The MCP server authenticates to SMT as a registered Competitive Service Provider (CSP).

### Plan Scraper / API
- **Data Source**: This component is responsible for providing a list of currently available electricity plans in Texas.
- **Implementation**: This could be implemented in two ways:
    1.  **Web Scraper**: A background process that regularly scrapes a public website like `powertochoose.org` and stores the plans in a database.
    2.  **Direct API**: An integration with a third-party API that provides electricity plan data.
- **API**: Exposes a simple endpoint for the agent to query for plans, filterable by region or utility.

---

## 5. Operational Considerations & Next Steps

- **CSP Registration**: The core of this project relies on the MCP Server operator being a registered Competitive Service Provider (CSP) with the Public Utility Commission of Texas (PUCT). This is a legal and administrative prerequisite.
- **Security**: The MCP Server must be highly secure, as it handles sensitive user consumption data. All communication should be over HTTPS, and it must comply with SMT's strict security requirements.
- **Scalability**: The MCP server should be designed to handle asynchronous data delivery from SMT (e.g., via FTPS for large data dumps) and manage a queue of requests from multiple agents.
- **Development Environments**: SMT provides a UAT (User Acceptance Testing) environment. All development and testing should be done against the UAT before moving to production.

## 6. Verified Documentation Links
- **Smart Meter Texas Interface Guide (PDF)**:  
  `https://www.smartmetertexas.com/commonapi/gethelpguide/help-guides/Smart_Meter_Texas_Interface_Guide.pdf`
- **Smart Meter Texas Portal**:  
  `https://www.smartmetertexas.com`
- **SMT API Endpoints (UAT)**:  
  `https://uatservices.smartmetertexas.net`
- **SMT API Endpoints (Production)**:  
  `https://services.smartmetertexas.net`
- **PUCT CSP Registration**:  
  `https://www.puc.texas.gov/industry/electric/business/csp.aspx`
