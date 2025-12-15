# 🧠 Travel Planning Agent

A planning-based AI agent that automatically generates and optimizes multi-day travel itineraries under soft constraints such as travel time, daily workload, and transportation mode.

This project focuses on **agent-style decision making** rather than simple route generation:
the agent explores multiple candidate itineraries, evaluates them under different policies, and selects the best plan with interpretable reasons.

---

## ✨ Key Features

- **World Modeling**
  - Structured representation of cities, spots, daily plans, and itineraries
- **Planning & Search**
  - Initial itinerary construction
  - Local search with move / swap operators
- **Soft Constraint Optimization**
  - Daily travel time limits
  - Experience quality penalties (e.g. too few spots in a day)
  - Interpretable scoring and self-check reports
- **Policy-Conditioned Planning**
  - Supports multiple transportation modes:
    - 🚶 WALK
    - 🚇 TRANSIT
    - 🚕 TAXI
  - Same planner, different world rules
- **Visualization**
  - Interactive map output using Folium
  - Day-by-day routes and markers

---

## 🧩 System Architecture

```text
User Choice (Transport Mode)
        ↓
Planner (Search + Local Edits)
        ↓
Soft Constraints Scorer
        ↓
World Geometry (Time / Distance)
        ↓
Best Itinerary + Explanation
