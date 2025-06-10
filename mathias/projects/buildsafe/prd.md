# Buildsafe AI Prototype - PRD (v1)

## 1. Introduction

This document outlines the requirements for the first version (v1) of the Buildsafe AI prototype. The goal is to create a Minimum Viable Product (MVP) demonstrating the core functionality of AI-assisted material calculation and pricing for a specific construction scenario.

## 2. Goals for V1

- Develop a functional prototype for calculating materials and costs for building a standard wooden deck ("Altan").
- Implement two core AI agents: one for quantity calculation and one for pricing.
- Provide a basic user interface flow mirroring the initial steps described in Henry's email.
- Use static/placeholder data for pricing in this initial version.
- Validate the concept of AI Augmentation for craftsmen in this domain.

## 3. Scope

### 3.1. In Scope

- **Project Type:** Nybyggnation av altan (New deck construction).
- **User Input:**
  - Deck dimensions (Length, Width, Height).
  - Decking material selection (Type, dimensions, board length - based on predefined options).
  - Railing selection (Type - including 'Inget', Post type/dimensions, Railing rule type/dimensions - based on predefined options).
  - Selection of one predefined building supplier (e.g., "Bauhaus Mock Data").
- **AI Agents:**
  - `MaterialQuantityAgent`: Calculates required quantities for decking, frame (joists/bearers), posts, foundations (concrete), basic fasteners (deck screws), and railing components based on standard Swedish practices and user inputs.
  - `MaterialPricingAgent`: Looks up list prices for the calculated materials using _static/mock_ price data for the selected supplier.
- **Output:** A summary view displaying:
  - User-provided project details.
  - An itemized list of calculated materials with quantities.
  - An itemized list of materials with unit prices and total costs (based on mock data).

### 3.2. Out of Scope for V1

- Other project types (Bathroom, Kitchen, etc.).
- Complex deck shapes or features (stairs, multiple levels).
- Detailed calculation of _all_ hardware (every specific screw type, bolt, bracket variation beyond basic estimates).
- Real-time price fetching from actual supplier databases/APIs.
- Integration with actual supplier discounts or craftsman-specific pricing.
- User accounts, project saving, or advanced UI features.
- Calculations for ground preparation, permits, or labor costs.

## 4. Core User Flow (V1 Scenario)

1.  User (Craftsman) opens the app/prototype.
2.  User selects: Tillbyggnad -> Altan -> Nybyggnation av altan.
3.  User inputs deck dimensions (L, W, H).
4.  User selects decking material type, dimensions, and board length from predefined options.
5.  User selects railing type (or 'Inget'), post details, and railing rule details from predefined options.
6.  User selects the mock supplier ("Bauhaus Mock Data").
7.  User confirms input.
8.  **Backend/AI Process:**
    - Input data is sent to `MaterialQuantityAgent`.
    - `MaterialQuantityAgent` calculates quantities based on rules and inputs.
    - The quantity list is sent to `MaterialPricingAgent`.
    - `MaterialPricingAgent` retrieves prices from the static mock data source.
9.  User is presented with a summary page showing inputs, calculated material quantities, and the itemized price list (list prices).

## 5. AI Agents

### 5.1. MaterialQuantityAgent

- **Purpose:** Calculate material quantities based on project specs.
- **Inputs:** Project type, dimensions, material selections.
- **Logic:** Based on predefined rules mimicking standard Swedish construction practices for decks.
- **Output:** Structured list of materials and quantities (JSON).
- **Instruction Prompt:** (See separate documentation/code comments for the full prompt)

### 5.2. MaterialPricingAgent

- **Purpose:** Retrieve list prices for materials from a specific supplier.
- **Inputs:** Material list (from Quantity Agent), Supplier Name.
- **Logic:** Lookup in a static data source (e.g., JSON file, hardcoded dictionary) for V1.
- **Output:** Structured list of materials with quantities, unit prices, and total costs (JSON).
- **Instruction Prompt:** (See separate documentation/code comments for the full prompt)

## 6. Data Requirements (V1)

- **Calculation Rules:** Predefined logic/rules for deck material calculation (embedded in the Quantity Agent or a configuration file).
- **Material Options:** Predefined lists of available materials (wood types, dimensions, railing types) for user selection.
- **Mock Price Data:** A static data structure (e.g., JSON) mapping material specifications to list prices for the mock supplier ("Bauhaus Mock Data").

## 7. Technology Considerations

- **Agent Framework:** Evaluate Vercel AI SDK, OpenAI Assistants API, or other suitable frameworks (e.g., Langchain, Agnetic) for managing agent interactions.
- **Frontend:** Basic web interface (React, Vue, Svelte, etc.) for user input and displaying results.
- **Backend (Optional):** May be needed depending on the chosen agent framework and complexity (e.g., Node.js, Python/Flask/FastAPI).
