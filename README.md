# AI Data Analysis Assistant

An intelligent Python-powered application that loads any CSV dataset, performs automatic exploratory data analysis, answers natural language questions, and creates meaningful visualizations.

## Features

- **CSV Loading** - Load any CSV file with automatic encoding detection
- **Auto Analysis** - Automatically detect column types and compute statistics
- **Natural Language QA** - Ask questions about your data in plain English
- **Smart Visualizations** - Automatically choose and create the best chart type
- **AI Insights** - Get concise, meaningful observations from Groq/OpenAI/Gemini
- **Error Handling** - Graceful handling of missing files, API failures, and more
- **Streamlit UI** - Beautiful dark-themed web interface with tabs, filters & charts

## Folder Structure

```
project/
|
+-- app.py               # Main entry point (Streamlit app)
+-- config.py            # Configuration (API keys, settings)
+-- dataset_loader.py    # CSV loading and validation
+-- analysis.py          # Data analysis and statistics
+-- utils.py             # Question answering engine
+-- visualization.py     # Chart creation
+-- ai_helper.py         # AI insight generation
+-- requirements.txt     # Python dependencies
+-- .env.example         # Environment variable template
+-- .gitignore           # Git ignore rules
+-- sample_dataset.csv   # Sample data for testing
+-- LICENSE              # MIT License
+-- README.md            # This file
|
+-- charts/              # Saved visualizations
|   +-- output_chart.png
|
+-- docs/                # Additional documentation
    +-- project_flow.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Azam-web788/Ai-Data-Analyzer-Hackathon.git
cd Ai-Data-Analyzer-Hackathon
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scriptsctivate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env and add your API key
```

Get a free API key from: [Groq Console](https://console.groq.com)

> 💡 **Already have a key?** The app checks `GROQ_API_KEY`, `API_KEY`, or `OPENAI_API_KEY` (in that order) for maximum compatibility.

## Usage

```bash
streamlit run app.py
```

1. Enter the path to your CSV file (or press Enter to use sample_dataset.csv)
2. View the automatic analysis results
3. Ask questions about your data (e.g., "What is the average price?")
4. Type 'exit' to generate a visualization
5. Receive AI-generated insights

### Example Questions

- "Which product generated the highest sales?"
- "What is the average price?"
- "Which city has the most orders?"
- "Which category appears most frequently?"
- "How many unique products are there?"
- "What is the maximum rating?"

## Technologies Used

- Python 3.8+
- **Pandas** - Data manipulation
- **NumPy** - Numerical computations
- **Matplotlib** - Data visualization
- **Streamlit** - Interactive web UI framework
- **python-dotenv** - Environment management
- **Groq / OpenAI / Gemini API** - AI-powered insights

## Deployment (Streamlit Cloud)

Deploy this app on [Streamlit Cloud](https://streamlit.io/cloud) for free:

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/Azam-web788/Ai-Data-Analyzer-Hackathon.git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"** → select your repository
4. Set **Main file path** to `app.py`
5. Click **"Deploy!"**

### 3. Set Up API Key (Secrets)

After deployment:
1. Go to your app's dashboard on Streamlit Cloud
2. Click **"Settings"** → **"Secrets"**
3. Add the following:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

4. Get a free key at: [console.groq.com](https://console.groq.com)
5. Your app will automatically restart with AI insights enabled!

> **Note:** The `.streamlit/secrets.toml` file in this repo is a **template only**. It is not read by Streamlit Cloud — you must paste its contents into the Secrets section of your app dashboard.

## Future Improvements

- Support for Excel, JSON, and other file formats
- Multiple chart types in a single run
- Interactive visualizations
- More advanced question understanding
- Export analysis as PDF report

## License

This project is licensed under the MIT License. See the LICENSE file for details.
