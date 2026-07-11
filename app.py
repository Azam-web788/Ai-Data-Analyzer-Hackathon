"""AI Data Analysis Assistant - Beautiful Streamlit Frontend"""
import streamlit as st
import pandas as pd
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dataset_loader import load_csv
from analysis import run_full_analysis
from utils import find_answer
from visualization import make_chart
# Clear stale bytecode cache to prevent module version mismatches
import shutil
_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '__pycache__')
try:
    if os.path.exists(_cache_dir):
        shutil.rmtree(_cache_dir)
except PermissionError:
    pass  # Windows may lock files; skip silently
from ai_helper import get_insight
import base64

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Data Analysis Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ─── Font & Base ─── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* ─── Headers ─── */
    h1, h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem !important;
    }
    
    /* ─── Glass Card ─── */
    .glass-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(102, 126, 234, 0.4);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
    }
    
    /* ─── Metric Cards ─── */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.5);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 4px;
    }
    
    /* ─── Sidebar ─── */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    [data-testid="stSidebar"] .st-emotion-cache-1cypcdb {
        padding: 2rem 1rem !important;
    }
    
    /* ─── File Uploader ─── */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 2px dashed rgba(102, 126, 234, 0.3) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(102, 126, 234, 0.6) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    /* ─── Buttons ─── */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* ─── Tabs ─── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px !important;
        background: rgba(255, 255, 255, 0.04) !important;
        border-radius: 12px !important;
        padding: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 8px 16px !important;
        color: rgba(255, 255, 255, 0.5) !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
    }
    
    /* ─── DataFrames ─── */
    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* ─── Info/Success/Warning boxes ─── */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    .stAlert > div {
        border-radius: 12px !important;
    }
    
    /* ─── Text inputs ─── */
    .stTextInput > div > div {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    .stTextInput > div > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* ─── Dividers ─── */
    hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
    }
    
    /* ─── Footer ─── */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.3);
        font-size: 0.8rem;
        padding: 20px 0;
        margin-top: 40px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    /* ─── Loader ─── */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* ─── Scrollbar ─── */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.5);
    }

    /* ─── Stat columns ─── */
    .stat-row {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        margin: 16px 0;
    }
    .stat-item {
        flex: 1;
        min-width: 120px;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 10px;
        padding: 12px 16px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .stat-item .label {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .stat-item .value {
        color: white;
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helper Functions ────────────────────────────────────────────────────────
def get_img_as_base64(img_path):
    """Convert image to base64 for inline display in markdown."""
    try:
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None


def render_metric(label, value, delta=None):
    """Render a styled metric card."""
    delta_html = ""
    if delta is not None:
        delta_class = "delta-up" if delta >= 0 else "delta-down"
        delta_html = f'<div class="{delta_class}">{"+" if delta >= 0 else ""}{delta}</div>'
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{value:,}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_headline(text, level=2):
    """Render a gradient headline."""
    size = {1: "2rem", 2: "1.5rem", 3: "1.2rem"}.get(level, "1.2rem")
    st.markdown(f"""
    <h{level} style="background: linear-gradient(135deg, #667eea, #764ba2); 
               -webkit-background-clip: text; 
               -webkit-text-fill-color: transparent; 
               background-clip: text;
               font-size: {size};
               font-weight: 700;
               margin-bottom: 16px;">{text}</h{level}>
    """, unsafe_allow_html=True)


# ─── Initialize Session State ───────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "chart_path" not in st.session_state:
    st.session_state.chart_path = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "question_history" not in st.session_state:
    st.session_state.question_history = []
if "use_sample" not in st.session_state:
    st.session_state.use_sample = False


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 24px;">
        <div style="font-size: 3rem; margin-bottom: 4px;">📊</div>
        <h3 style="background: linear-gradient(135deg, #667eea, #764ba2);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   background-clip: text;
                   margin: 0;">AI Data Analysis</h3>
        <p style="color: rgba(255,255,255,0.4); font-size: 0.8rem; margin: 4px 0 0;">
            Upload. Analyze. Discover.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Data source options
    render_headline("Data Source", 3)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📁 Upload CSV", width='stretch', 
                     type="primary" if not st.session_state.use_sample else "secondary"):
            st.session_state.use_sample = False
            st.session_state.data = None
            st.session_state.analysis = None
            st.rerun()
    with col2:
        if st.button("📦 Sample Data", width='stretch',
                     type="primary" if st.session_state.use_sample else "secondary"):
            st.session_state.use_sample = True
            st.rerun()
    
    if not st.session_state.use_sample:
        uploaded = st.file_uploader("Choose a CSV file", type=["csv"], label_visibility="collapsed")
        # Only process file if data hasn't been loaded yet (guard against re-processing on rerun)
        if uploaded is not None and st.session_state.data is None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded.getvalue())
                tmp_path = tmp.name
            data = load_csv(tmp_path)
            os.unlink(tmp_path)
            if data is not None:
                st.session_state.data = data
                with st.spinner("Analyzing..."):
                    st.session_state.analysis = run_full_analysis(data)
                st.success(f"✅ Loaded: {len(data)} rows × {len(data.columns)} cols")
    else:
        sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_dataset.csv")
        if os.path.exists(sample_path) and st.session_state.data is None:
            data = load_csv(sample_path)
            if data is not None:
                st.session_state.data = data
                if st.session_state.analysis is None:
                    with st.spinner("Analyzing..."):
                        st.session_state.analysis = run_full_analysis(data)
                    st.success(f"✅ Loaded sample: {len(data)} rows × {len(data.columns)} cols")
    
    # Show dataset summary if loaded
    if st.session_state.data is not None:
        st.markdown("---")
        render_headline("Dataset Info", 3)
        df = st.session_state.data
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-item">
                <div class="label">Rows</div>
                <div class="value">{len(df):,}</div>
            </div>
            <div class="stat-item">
                <div class="label">Columns</div>
                <div class="value">{len(df.columns)}</div>
            </div>
            <div class="stat-item">
                <div class="label">Missing</div>
                <div class="value">{st.session_state.analysis['missing']:,}</div>
            </div>
            <div class="stat-item">
                <div class="label">Duplicates</div>
                <div class="value">{st.session_state.analysis['dupes']:,}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Column types
        nums = st.session_state.analysis['nums']
        cats = st.session_state.analysis['cats']
        dates = st.session_state.analysis['dates']
        st.markdown(f"""
        <div style="margin-top: 8px;">
            <span style="background: rgba(102,126,234,0.2); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">
                🔢 {len(nums)} numeric
            </span>
            <span style="background: rgba(118,75,162,0.2); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin-left: 4px;">
                🏷️ {len(cats)} categorical
            </span>
            <span style="background: rgba(255,193,7,0.2); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin-left: 4px;">
                📅 {len(dates)} date
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="footer" style="border: none; margin-top: 0; padding: 0; font-size: 0.7rem;">
        Built with ❤️ using Streamlit
    </div>
    """, unsafe_allow_html=True)


# ─── Main Content ────────────────────────────────────────────────────────────
# Hero section
st.markdown("""
<div style="text-align: center; padding: 40px 0 20px;">
    <h1 style="font-size: 2.8rem; margin: 0;">AI Data Analysis Assistant</h1>
    <p style="color: rgba(255,255,255,0.5); font-size: 1.1rem; margin: 8px 0 0;">
        Upload any CSV and unlock insights instantly ✨
    </p>
</div>
""", unsafe_allow_html=True)

if st.session_state.data is None:
    # ─── Landing / Empty State ──────────────────────────────────────────────
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 60px 40px;">
        <div style="font-size: 4rem; margin-bottom: 16px;">📂</div>
        <h2 style="color: white; margin: 0 0 8px;">Ready to analyze your data?</h2>
        <p style="color: rgba(255,255,255,0.5); max-width: 500px; margin: 0 auto 24px;">
            Upload a CSV file from the sidebar or try our sample dataset to see 
            the power of AI-driven data analysis.
        </p>
        <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
            <span style="background: rgba(102,126,234,0.15); padding: 8px 16px; border-radius: 20px; font-size: 0.85rem;">
                🔍 Auto-detect column types
            </span>
            <span style="background: rgba(102,126,234,0.15); padding: 8px 16px; border-radius: 20px; font-size: 0.85rem;">
                📈 Smart visualizations
            </span>
            <span style="background: rgba(102,126,234,0.15); padding: 8px 16px; border-radius: 20px; font-size: 0.85rem;">
                🤖 AI-powered insights
            </span>
            <span style="background: rgba(102,126,234,0.15); padding: 8px 16px; border-radius: 20px; font-size: 0.85rem;">
                💬 Natural language queries
            </span>
        </div>
        <div style="margin-top: 24px;">
            <p style="color: rgba(255,255,255,0.3); font-size: 0.85rem;">
                Or press <strong>"📦 Sample Data"</strong> in the sidebar to try now
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 2.5rem;">📊</div>
            <h3 style="color: white; margin: 8px 0;">Smart Dashboard</h3>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.9rem; margin: 0;">
                Auto-generated metrics, charts, and summaries at a glance
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 2.5rem;">💬</div>
            <h3 style="color: white; margin: 8px 0;">Ask Questions</h3>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.9rem; margin: 0;">
                Ask anything in plain English & get instant answers
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 2.5rem;">🧠</div>
            <h3 style="color: white; margin: 8px 0;">AI Insights</h3>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.9rem; margin: 0;">
                Get LLM-powered findings, suggestions & patterns
            </p>
        </div>
        """, unsafe_allow_html=True)

else:
    # ─── Data Loaded: Tabs ───────────────────────────────────────────────────
    data = st.session_state.data
    analysis = st.session_state.analysis
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", "📋 Data Explorer", "📈 Visualizations", 
        "💬 Ask Questions", "🤖 AI Insights"
    ])
    
    # ─── TAB 1: Dashboard ──────────────────────────────────────────────────
    with tab1:
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: white; margin: 0 0 16px;">📊 Overview</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Metric row
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            render_metric("Total Rows", len(data))
        with mcol2:
            render_metric("Columns", len(data.columns))
        with mcol3:
            render_metric("Missing Values", analysis['missing'])
        with mcol4:
            render_metric("Duplicate Rows", analysis['dupes'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Two columns: numeric stats + categorical stats
        lcol, rcol = st.columns(2)
        
        with lcol:
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: white; margin: 0 0 12px;">🔢 Numeric Columns</h4>
            """, unsafe_allow_html=True)
            
            if analysis['num_stats']:
                for s in analysis['num_stats']:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.04); border-radius: 8px; padding: 12px; margin-bottom: 8px;
                                border: 1px solid rgba(255,255,255,0.06);">
                        <div style="font-weight: 600; color: #667eea; margin-bottom: 4px;">{s['col']}</div>
                        <div style="display: flex; gap: 12px; font-size: 0.85rem; color: rgba(255,255,255,0.6); flex-wrap: wrap;">
                            <span>Mean: <strong style="color:white;">{s['mean']}</strong></span>
                            <span>Median: <strong style="color:white;">{s['median']}</strong></span>
                            <span>Min: <strong style="color:white;">{s['min']}</strong></span>
                            <span>Max: <strong style="color:white;">{s['max']}</strong></span>
                            <span>Count: <strong style="color:white;">{s['count']:,}</strong></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No numeric columns found")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with rcol:
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: white; margin: 0 0 12px;">🏷️ Categorical Columns</h4>
            """, unsafe_allow_html=True)
            
            if analysis['cat_stats']:
                for s in analysis['cat_stats']:
                    top_items = list(s['top'].items())[:3]
                    top_str = ", ".join([f"<strong>{k}</strong> ({v})" for k, v in top_items])
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.04); border-radius: 8px; padding: 12px; margin-bottom: 8px;
                                border: 1px solid rgba(255,255,255,0.06);">
                        <div style="font-weight: 600; color: #764ba2; margin-bottom: 4px;">{s['col']}</div>
                        <div style="font-size: 0.85rem; color: rgba(255,255,255,0.6);">
                            <span>Unique: <strong style="color:white;">{s['unique']:,}</strong></span>
                            <span style="margin-left: 12px;">Top: {top_str}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No categorical columns found")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # ─── TAB 2: Data Explorer ──────────────────────────────────────────────
    with tab2:
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: white; margin: 0 0 16px;">📋 Data Explorer</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Filters
        with st.expander("🔍 Search & Filter", expanded=True):
            search = st.text_input("Search across all columns", placeholder="Type to filter...")
            
            if len(data.columns) > 1:
                filter_col = st.selectbox("Filter by column", ["All Columns"] + list(data.columns))
            else:
                filter_col = "All Columns"
        
        # Apply search filter
        if search:
            mask = pd.Series([False] * len(data))
            if filter_col != "All Columns":
                mask = data[filter_col].astype(str).str.contains(search, case=False, na=False)
            else:
                for col in data.columns:
                    mask |= data[col].astype(str).str.contains(search, case=False, na=False)
            filtered = data[mask]
        else:
            filtered = data
        
        st.markdown(f"""
        <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin-bottom: 8px;">
            Showing {len(filtered):,} of {len(data):,} rows
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(filtered, width='stretch', height=400)
        
        # Quick stats
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: white; margin: 0 0 8px;">📊 Column Summary</h4>
            """, unsafe_allow_html=True)
            dtype_df = pd.DataFrame({
                "Column": data.dtypes.index,
                "Type": data.dtypes.values.astype(str),
                "Missing": data.isnull().sum().values,
                "Unique": [data[c].nunique() for c in data.columns],
            })
            st.dataframe(dtype_df, width='stretch', height=200)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: white; margin: 0 0 8px;">📈 Quick Distribution</h4>
            """, unsafe_allow_html=True)
            num_cols = analysis['nums']
            if num_cols:
                dist_col = st.selectbox("Select column", num_cols, key="dist_col")
                col_data = data[dist_col].dropna()
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 2rem; font-weight: 700; color: white;">
                        {col_data.mean():.2f}
                    </div>
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">Mean {dist_col}</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 12px; font-size: 0.85rem;">
                    <span>Min: <strong style="color:white;">{col_data.min():.2f}</strong></span>
                    <span>Max: <strong style="color:white;">{col_data.max():.2f}</strong></span>
                    <span>Std: <strong style="color:white;">{col_data.std():.2f}</strong></span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No numeric columns for distribution")
            st.markdown("</div>", unsafe_allow_html=True)
    
    # ─── TAB 3: Visualizations ─────────────────────────────────────────────
    with tab3:
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: white; margin: 0 0 16px;">📈 Auto-Generated Visualizations</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Generate Chart", width='stretch', type="primary"):
            with st.spinner("Creating visualization..."):
                chart_path = make_chart(data, analysis)
                if chart_path and os.path.exists(chart_path):
                    st.session_state.chart_path = chart_path
                    st.success("✅ Chart generated!")
                    st.rerun()
                else:
                    st.error("Could not generate chart")
        
        if st.session_state.chart_path and os.path.exists(st.session_state.chart_path):
            img_b64 = get_img_as_base64(st.session_state.chart_path)
            if img_b64:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.04); border-radius: 12px; padding: 16px; margin-top: 12px;
                            border: 1px solid rgba(255,255,255,0.06);">
                    <img src="data:image/png;base64,{img_b64}" style="width: 100%; border-radius: 8px;" />
                </div>
                """, unsafe_allow_html=True)
        
        # Chart type info
        nums = analysis['nums']
        cats = analysis['cats']
        
        st.markdown("""
        <div class="glass-card" style="margin-top: 20px;">
            <h4 style="color: white; margin: 0 0 8px;">🎯 Chart Suggestions</h4>
        """, unsafe_allow_html=True)
        
        suggestions = []
        if cats and nums:
            suggestions.append(f"📊 **Bar Chart**: {nums[0]} by {cats[0]}")
        if len(nums) >= 2:
            suggestions.append(f"🔵 **Scatter Plot**: {nums[1]} vs {nums[0]}")
        if nums:
            suggestions.append(f"📈 **Histogram**: Distribution of {nums[0]}")
        if cats:
            suggestions.append(f"📊 **Bar Chart**: Frequency of {cats[0]}")
        
        for s in suggestions:
            st.markdown(f"- {s}")
        
        if not suggestions:
            st.info("No chart suggestions available")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ─── TAB 4: Ask Questions ──────────────────────────────────────────────
    with tab4:
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: white; margin: 0 0 8px;">💬 Ask Questions in Plain English</h3>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin: 0;">
                Try: "What is the average price?", "Which category is most common?", 
                "What is the highest rating?"
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick question chips
        st.markdown("""
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px;">
        """, unsafe_allow_html=True)
        
        suggestions_q = []
        for c in analysis['nums'][:2]:
            suggestions_q.append(f"What is the average {c}?")
            suggestions_q.append(f"What is the max {c}?")
        for c in analysis['cats'][:2]:
            suggestions_q.append(f"Which {c} is most common?")
        suggestions_q.append("How many rows are there?")
        suggestions_q.append("How many unique values?")
        
        # Show suggestion chips
        cols = st.columns(3)
        for i, sq in enumerate(suggestions_q[:6]):
            with cols[i % 3]:
                if st.button(f"💡 {sq}", width='stretch', key=f"qs_{i}"):
                    # Treat as if user typed this question
                    q = sq
                    answer = find_answer(data, q)
                    st.session_state.question_history.append((q, answer))
                    st.rerun()
        
        # Question input
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            q = st.text_input("Type your question", placeholder="e.g., What is the average price?", label_visibility="collapsed")
        with col2:
            ask_btn = st.button("🔍 Ask", width='stretch', type="primary")
        
        if ask_btn and q:
            with st.spinner("Finding answer..."):
                answer = find_answer(data, q)
                st.session_state.question_history.append((q, answer))
        
        # Show question history
        if st.session_state.question_history:
            st.markdown("---")
            st.markdown("<h4 style='color: white;'>📝 Question History</h4>", unsafe_allow_html=True)
            for i, (question, answer) in enumerate(reversed(st.session_state.question_history[-10:])):
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.04); border-radius: 10px; padding: 12px 16px; margin-bottom: 8px;
                            border-left: 3px solid #667eea;">
                    <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; font-weight: 500;">❓ {question}</div>
                    <div style="color: white; font-size: 1rem; margin-top: 4px;">💡 {answer}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # ─── TAB 5: AI Insights ────────────────────────────────────────────────
    with tab5:
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: white; margin: 0 0 8px;">🤖 AI-Powered Insights</h3>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin: 0;">
                Get intelligent analysis using LLMs (Groq, OpenAI, or Gemini).
                Set your <strong>API_KEY</strong> in the <code>.env</code> file.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("✨ Generate AI Insights", width='stretch', type="primary"):
                with st.spinner("🤔 AI is analyzing your data..."):
                    insight = get_insight(analysis, data)
                if insight:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.15));
                                border: 1px solid rgba(102,126,234,0.2);
                                border-radius: 12px; padding: 24px; margin-top: 12px;">
                        <div style="font-size: 1.1rem; color: white; line-height: 1.6;">{insight}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("""
                    ⚠️ No API key configured. To enable AI insights:
                    1. Create a `.env` file in the project root
                    2. Add: `API_KEY=your_groq_api_key`
                    3. Get a free key at: https://console.groq.com
                    """)
        
        with col2:
            st.markdown("""
            <div class="glass-card" style="padding: 16px;">
                <h4 style="color: white; margin: 0 0 8px; font-size: 0.9rem;">📋 Analysis Summary</h4>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="font-size: 0.85rem; color: rgba(255,255,255,0.6);">
                <p><strong style="color:white;">{analysis['rows']:,}</strong> rows</p>
                <p><strong style="color:white;">{analysis['cols']}</strong> columns</p>
                <p><strong style="color:white;">{analysis['missing']:,}</strong> missing values</p>
                <p><strong style="color:white;">{analysis['dupes']:,}</strong> duplicates</p>
                <p><strong style="color:white;">{len(analysis['nums'])}</strong> numeric columns</p>
                <p><strong style="color:white;">{len(analysis['cats'])}</strong> categorical columns</p>
                <p><strong style="color:white;">{len(analysis['dates'])}</strong> date columns</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    AI Data Analysis Assistant &mdash; Built with Streamlit &hearts;
</div>
""", unsafe_allow_html=True)
