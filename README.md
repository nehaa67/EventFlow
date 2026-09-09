# EventFlow

EventFlow is an AI-powered event management and crowd intelligence platform designed to help organizers understand what is happening during an event and make better decisions before small issues become major problems.

It combines real-time event data, crowd prediction, risk analysis, simulation, and actionable insights in one dashboard.

## What EventFlow Does

EventFlow focuses on four main questions:

- **What is happening?**  
  Understand the current state of an event and crowd.

- **What could happen next?**  
  Predict crowd levels at different time intervals.

- **What could go wrong?**  
  Identify potential risks and high-risk situations.

- **What should we do about it?**  
  Analyze possible causes and support better operational decisions.

## Key Features

### Crowd Prediction
Predicts expected crowd levels for upcoming time intervals using trained machine learning models.

### Risk Analysis
Identifies potential risks based on event conditions and crowd behaviour.

### Root Cause Analysis
Helps identify the factors contributing to a detected issue instead of only showing the problem.

### Event Simulation
Allows organizers to explore different scenarios and understand how changes could affect the event.

### Event State Monitoring
Provides a structured view of the current event state so organizers can quickly understand important conditions.

### Interactive Dashboard
A React-based interface brings the predictions, risks, simulations, and event insights together in one place.

## Tech Stack

### Frontend
- React
- Vite
- Tailwind CSS
- JavaScript

### Backend
- Python
- FastAPI
- Machine Learning

### Database
- PostgreSQL

### Deployment
- Vercel
- Render
- Docker

## Project Structure

```text
EventFlow/
├── backend/
│   ├── app/
│   ├── data/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── database/
│   └── final.sql
│
├── scripts/
├── docker-compose.yml
└── render.yaml
