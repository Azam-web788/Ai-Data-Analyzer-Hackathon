# Project Flow & Architecture

## How the Application Works

This document explains the flow of data and control through the application.

## Execution Flow

```
START
  |
  v
[1] app.py - Streamlit Entry Point
  |  - Renders dark-themed web UI
  |  - Handles sidebar, tabs, file upload
  |
  v
[2] dataset_loader.py - Load & Validate CSV
  |  - Checks file exists
  |  - Tries multiple encodings
  |  - Returns DataFrame
  |
  v
[3] analysis.py - Perform Full Analysis
  |  - Detect column types (numeric/categorical/date)
  |  - Compute statistics for each column
  |  - Generate correlation matrix
  |
  v
[4] utils.py - Answer User Questions
  |  - Parse natural language question
  |  - Use Pandas to compute answer
  |  - Display answer in web UI
  |  - Suggest follow-up questions
  |
  v
[5] visualization.py - Create Chart
  |  - Determine best chart type
  |  - Create and save chart as PNG
  |
  v
[6] ai_helper.py - Generate Insights
  |  - Build summary from analysis results
  |  - Send summary to LLM API (Groq/OpenAI/Gemini)
  |  - Display AI-generated insight
  |
  v
END - Interactive Dashboard
```

## Module Responsibilities

| Module | Purpose |
|--------|---------|
| main.py | Entry point, orchestrates the workflow |
| config.py | Environment variables and settings |
| dataset_loader.py | Load and validate CSV files |
| analysis.py | Data analysis and statistics |
| utils.py | Natural language question answering |
| visualization.py | Chart creation and saving |
| ai_helper.py | LLM-based insight generation |

## Design Decisions

1. **No external framework** - Keeps the project lightweight and easy to understand
2. **Modular design** - Each file has a single, clear responsibility
3. **LLM efficiency** - Only summary stats sent to API, never full dataset
4. **Pandas-first QA** - Questions answered with Python first, LLM as fallback
5. **Error resilience** - Every failure path has a meaningful message
