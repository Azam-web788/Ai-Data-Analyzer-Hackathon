"""AI Data Analysis Assistant - Beautiful Streamlit Frontend"""
import streamlit as st
import pandas as pd
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dataset_loader import load_csv, load_excel
from analysis import run_full_analysis
from utils import find_answer, detect_chart_intent
from visualization import make_chart, make_custom_chart, CHART_TYPES, generate_dashboard
# Clear stale bytecode cache to prevent module version mismatches
import shutil
_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '__pycache__')
try:
    if os.path.exists(_cache_dir):
        shutil.rmtree(_cache_dir)
except PermissionError:
    pass  # Windows may lock files; skip silently
import base64

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Analysis Assistant",
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


def voice_input_component():
    """Render speech recognition and directly fill the text input.
    Uses st.markdown to inject JS directly into the page DOM (no iframe).
    """
    js_code = """
    <div id="voice-ui" style="text-align: center; padding: 8px;">
        <div id="voice-status" style="color: rgba(255,255,255,0.6); font-size: 13px; margin-bottom: 8px;">
            🎤 Speak now...
        </div>
        <div style="margin: 0 auto; width: 24px; height: 24px;">
            <span style="display: inline-block; width: 3px; height: 100%; margin: 0 2px; background: #e74c3c; animation: vb-wave 1s ease-in-out infinite; border-radius: 2px;"></span>
            <span style="display: inline-block; width: 3px; height: 100%; margin: 0 2px; background: #e74c3c; animation: vb-wave 1s ease-in-out 0.2s infinite; border-radius: 2px;"></span>
            <span style="display: inline-block; width: 3px; height: 100%; margin: 0 2px; background: #e74c3c; animation: vb-wave 1s ease-in-out 0.4s infinite; border-radius: 2px;"></span>
            <span style="display: inline-block; width: 3px; height: 100%; margin: 0 2px; background: #e74c3c; animation: vb-wave 1s ease-in-out 0.6s infinite; border-radius: 2px;"></span>
            <span style="display: inline-block; width: 3px; height: 100%; margin: 0 2px; background: #e74c3c; animation: vb-wave 1s ease-in-out 0.8s infinite; border-radius: 2px;"></span>
        </div>
        <style>
            @keyframes vb-wave {
                0%, 100% { transform: scaleY(0.3); }
                50% { transform: scaleY(0.8); }
            }
        </style>
    </div>
    <script>
        (function() {
            // Remove existing voice-ui if already present
            var existing = document.getElementById('voice-ui');
            if (existing) existing.remove();

            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                document.body.insertAdjacentHTML('beforeend',
                    '<div id="voice-err" style="color:#e74c3c;text-align:center;padding:8px;">Not supported</div>');
                return;
            }

            var recognition = new SpeechRecognition();
            recognition.lang = 'en-US';
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onresult = function(event) {
                var text = event.results[0][0].transcript;
                // Find the text input by placeholder
                var tries = 0;
                var findInput = setInterval(function() {
                    var input = document.querySelector('input[placeholder="e.g., What is the average price?"]');
                    if (input) {
                        clearInterval(findInput);
                        // Use native value setter to trigger React
                        var nativeSetter = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype, 'value'
                        ).set;
                        nativeSetter.call(input, text);
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        // Also trigger change event
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        // Click the Ask button
                        var askBtns = document.querySelectorAll('button');
                        for (var i = 0; i < askBtns.length; i++) {
                            if (askBtns[i].textContent.trim() === '🔍 Ask') {
                                askBtns[i].click();
                                break;
                            }
                        }
                    }
                    tries++;
                    if (tries > 20) clearInterval(findInput); // 2 second timeout
                }, 100);
            };

            recognition.onerror = function(event) {
                console.log('Voice error:', event.error);
            };

            recognition.start();
        })();
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)
    return None  # JS handles everything directly


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
if "dashboard_charts" not in st.session_state:
    st.session_state.dashboard_charts = []
if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = "dataset"
if "pdf_report_bytes" not in st.session_state:
    st.session_state.pdf_report_bytes = None
if "report_notes" not in st.session_state:
    st.session_state.report_notes = ""
if "voice_triggered" not in st.session_state:
    st.session_state.voice_triggered = False



# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 24px;">
        <div style="font-size: 3rem; margin-bottom: 4px;">📊</div>
        <h3 style="background: linear-gradient(135deg, #667eea, #764ba2);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   background-clip: text;
                   margin: 0;">Data Analysis</h3>
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
        if st.button("📁 Upload CSV/Excel", width='stretch', 
                     type="primary" if not st.session_state.use_sample else "secondary"):
            st.session_state.use_sample = False
            st.session_state.data = None
            st.session_state.analysis = None
            st.session_state.dashboard_charts = []
            st.session_state.dataset_name = "dataset"
            st.session_state.pdf_report_bytes = None
            st.session_state.report_notes = ""
            st.rerun()
    with col2:
        if st.button("📦 Sample Data", width='stretch',
                     type="primary" if st.session_state.use_sample else "secondary"):
            st.session_state.use_sample = True
            st.rerun()
    
    if not st.session_state.use_sample:
        uploaded = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"], label_visibility="collapsed")
        # Only process file if data hasn't been loaded yet (guard against re-processing on rerun)
        if uploaded is not None and st.session_state.data is None:
            # Detect file type from extension
            fname = uploaded.name.lower()
            if fname.endswith('.csv'):
                suffix = '.csv'
                loader = load_csv
            else:
                suffix = '.xlsx' if fname.endswith('.xlsx') else '.xls'
                loader = load_excel
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded.getvalue())
                tmp_path = tmp.name
            data = loader(tmp_path)
            os.unlink(tmp_path)
            if data is not None:
                st.session_state.data = data
                st.session_state.dashboard_charts = []
                st.session_state.dataset_name = os.path.splitext(uploaded.name)[0]
                with st.spinner("Analyzing..."):
                    st.session_state.analysis = run_full_analysis(data)
                st.success(f"✅ Loaded: {len(data)} rows × {len(data.columns)} cols")
    else:
        sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_dataset.csv")
        if os.path.exists(sample_path) and st.session_state.data is None:
            data = load_csv(sample_path)
            if data is not None:
                st.session_state.data = data
                st.session_state.dashboard_charts = []
                st.session_state.dataset_name = "sample_dataset"
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
    <h1 style="font-size: 2.8rem; margin: 0;">Data Analysis Assistant</h1>
    <p style="color: rgba(255,255,255,0.5); font-size: 1.1rem; margin: 8px 0 0;">
        Upload any CSV or Excel and unlock insights instantly ✨
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
            Upload a CSV or Excel file from the sidebar or try our sample dataset to see 
            the power of data analysis.
        </p>
        <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
            <span style="background: rgba(102,126,234,0.15); padding: 8px 16px; border-radius: 20px; font-size: 0.85rem;">
                🔍 Auto-detect column types
            </span>
            <span style="background: rgba(102,126,234,0.15); padding: 8px 16px; border-radius: 20px; font-size: 0.85rem;">
                📈 Smart visualizations
            </span>
            <span style="background: rgba(102,126,234,0.15); padding: 8px 16px; border-radius: 20px; font-size: 0.85rem;">
                📊 Statistical analysis
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
            <div style="font-size: 2.5rem;">📈</div>
            <h3 style="color: white; margin: 8px 0;">Visual Insights</h3>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.9rem; margin: 0;">
                Auto-generated charts and visualizations for quick understanding
            </p>
        </div>
        """, unsafe_allow_html=True)

else:
    # ─── Data Loaded: Tabs ───────────────────────────────────────────────────
    data = st.session_state.data
    analysis = st.session_state.analysis
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard", "📋 Data Explorer", "📈 Visualizations", "💬 Ask Questions"
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
        
        # ─── Dashboard Grid ────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: white; margin: 0 0 16px;">📊 Multi-Chart Dashboard</h3>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin: 0;">
                Auto-generated 2×2 grid of the most insightful charts for your data
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate Dashboard button
        dcol1, dcol2, dcol3 = st.columns([1, 2, 1])
        with dcol2:
            if st.button("🚀 Generate Dashboard Grid", width='stretch', type='primary'):
                with st.spinner("Generating dashboard with multiple charts..."):
                    charts = generate_dashboard(data, analysis, count=4)
                    if charts:
                        st.session_state.dashboard_charts = charts
                        st.success(f"✅ Dashboard generated with {len(charts)} charts!")
                        st.rerun()
                    else:
                        st.error("Could not generate dashboard charts")
        
        # Display dashboard grid
        if st.session_state.dashboard_charts:
            st.markdown("<br>", unsafe_allow_html=True)
            charts = st.session_state.dashboard_charts
            
            # 2×2 grid: iterate in pairs
            for row_idx in range(0, len(charts), 2):
                row_charts = charts[row_idx:row_idx+2]
                cols = st.columns(2)
                for col_idx, (title, path) in enumerate(row_charts):
                    if os.path.exists(path):
                        img_b64 = get_img_as_base64(path)
                        if img_b64:
                            with cols[col_idx]:
                                st.markdown(f"""
                                <div style="background: rgba(255,255,255,0.04); border-radius: 12px; padding: 12px;
                                            border: 1px solid rgba(255,255,255,0.06); margin-bottom: 16px;">
                                    <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem; font-weight: 600; margin: 0 0 8px;">{title}</p>
                                    <img src="data:image/png;base64,{img_b64}" style="width: 100%; border-radius: 8px;" />
                                </div>
                                """, unsafe_allow_html=True)
            
            # ── Custom notes for PDF ────────────────────────────────────
            with st.expander("📝 Add Custom Notes for PDF Report", expanded=False):
                st.markdown("<p style='color: rgba(255,255,255,0.5); font-size:0.8rem; margin-bottom:4px;'>These notes will appear in the exported PDF report.</p>", unsafe_allow_html=True)
                st.text_area(
                    "Report Notes",
                    key="report_notes",
                    placeholder="Add your insights, observations, or conclusions here...\n\nExample:\n- The sales data shows a clear upward trend in Q3.\n- Marketing spend correlates strongly with revenue growth.\n- Recommend increasing budget for top-performing categories.",
                    height=150,
                    label_visibility="collapsed"
                )

            # Export & clear buttons
            st.markdown("<br>", unsafe_allow_html=True)
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                if st.button("📄 Export PDF Report", width='stretch', type='primary'):
                    with st.spinner("Generating PDF report..."):
                        from report import generate_pdf_report
                        pdf_path = generate_pdf_report(
                            data, analysis,
                            dashboard_charts=st.session_state.dashboard_charts,
                            dataset_name=st.session_state.dataset_name,
                            custom_notes=st.session_state.report_notes
                        )
                        if pdf_path and os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as f:
                                st.session_state.pdf_report_bytes = f.read()
                            st.success("✅ PDF report generated!")
                        else:
                            st.error("Could not generate PDF report")
            with exp_col2:
                if st.button("🗑️ Clear Dashboard", width='stretch', type='secondary'):
                    st.session_state.dashboard_charts = []
                    st.session_state.pdf_report_bytes = None
                    st.rerun()

            # Download button (always visible when PDF bytes exist)
            if st.session_state.pdf_report_bytes is not None:
                st.download_button(
                    "💾 Download PDF Report",
                    st.session_state.pdf_report_bytes,
                    file_name=f"{st.session_state.dataset_name}_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_pdf"
                )
    
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
        nums = analysis['nums']
        cats = analysis['cats']
        dates = analysis['dates']
        all_cols = list(data.columns)

        st.markdown("""
        <div class="glass-card">
            <h3 style="color: white; margin: 0 0 16px;">📈 Chart Studio</h3>
            <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin: 0;">
                Pick a chart type, choose columns, and visualize your data your way
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ── Quick suggestion chips ──────────────────────────────────────────
        st.markdown("<p style='color: rgba(255,255,255,0.5); font-size:0.85rem; margin-bottom:4px;'>⚡ Quick Charts</p>", unsafe_allow_html=True)
        suggestions = []
        if cats and nums:
            suggestions.append(('bar', cats[0], nums[0], f'📊 {nums[0]} by {cats[0]}'))
            suggestions.append(('box', cats[0], nums[0], f'📦 {nums[0]} by {cats[0]}'))
            suggestions.append(('violin', cats[0], nums[0], f'🎻 {nums[0]} by {cats[0]}'))
        if len(nums) >= 2:
            suggestions.append(('scatter', nums[0], nums[1], f'🔵 {nums[1]} vs {nums[0]}'))
            suggestions.append(('line', nums[0], nums[1], f'📉 {nums[1]} over {nums[0]}'))
        if nums:
            suggestions.append(('histogram', nums[0], None, f'📈 {nums[0]} Distribution'))
        if cats:
            suggestions.append(('pie', cats[0], None, f'🥧 {cats[0]} Proportion'))
        if len(nums) >= 2:
            suggestions.append(('heatmap', None, None, '🔥 Correlation'))

        # Render suggestion buttons in rows of 3
        for i in range(0, len(suggestions), 3):
            row = suggestions[i:i+3]
            cols = st.columns(3)
            for j, (sty, xc, yc, lbl) in enumerate(row):
                with cols[j]:
                    if st.button(lbl, width='stretch', key=f'viz_sug_{i+j}', type='secondary'):
                        with st.spinner(f"Generating {lbl.split(' ',1)[1]}..."):
                            chart_path = make_custom_chart(data, sty, xc, yc)
                            if chart_path and os.path.exists(chart_path):
                                st.session_state.chart_path = chart_path
                                st.rerun()
                            else:
                                st.error('Could not generate chart')

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Custom chart builder ────────────────────────────────────────────
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: white; margin: 0 0 12px;">🎨 Build Custom Chart</h4>
        """, unsafe_allow_html=True)

        ccol1, ccol2, ccol3 = st.columns(3)

        with ccol1:
            chart_keys = list(CHART_TYPES.keys())
            chart_labels = list(CHART_TYPES.values())
            selected_chart = st.selectbox("Chart Type", chart_labels, index=0,
                                           key='chart_type_sel')
            chart_style = chart_keys[chart_labels.index(selected_chart)]

        with ccol2:
            # Determine X column options based on chart type
            if chart_style in ('histogram',):
                x_opts = nums
            elif chart_style in ('heatmap', 'pairplot'):
                x_opts = []
                x_col = st.selectbox("X Column", ['(auto)'], key=f'chart_x_col_{chart_style}')
            elif chart_style in ('bar', 'pie', 'box', 'violin'):
                x_opts = cats or nums
            else:
                x_opts = all_cols

            if chart_style not in ('heatmap', 'pairplot'):
                x_col = st.selectbox("X Column", x_opts if x_opts else ['(none)'],
                                     key=f'chart_x_col_{chart_style}')
            else:
                x_col = None

        with ccol3:
            # Determine Y column options based on chart type
            if chart_style in ('histogram',):
                y_opts = []
                y_col = st.selectbox("Y Column", ['(none)'], key=f'chart_y_col_{chart_style}')
            elif chart_style in ('bar', 'pie', 'box', 'violin'):
                y_opts = nums
            elif chart_style in ('scatter', 'line', 'area'):
                y_opts = nums if nums else ['(none)']
            elif chart_style in ('heatmap', 'pairplot'):
                y_opts = []
                y_col = st.selectbox("Y Column", ['(auto)'], key=f'chart_y_col_{chart_style}')
            else:
                y_opts = []

            if chart_style not in ('histogram', 'heatmap', 'pairplot'):
                y_col = st.selectbox("Y Column", y_opts if y_opts else ['(none)'],
                                     key=f'chart_y_col_{chart_style}')
            else:
                y_col = None

        # Generate button
        st.markdown("<br>", unsafe_allow_html=True)
        gen_col1, gen_col2, gen_col3 = st.columns([1, 2, 1])
        with gen_col2:
            if st.button("🎨 Generate Chart", width='stretch', type='primary'):
                with st.spinner("Creating visualization..."):
                    # Validate columns
                    x = x_col if x_col and x_col != '(none)' and x_col != '(auto)' else None
                    y = y_col if y_col and y_col != '(none)' and y_col != '(auto)' else None
                    chart_path = make_custom_chart(data, chart_style, x, y)
                    if chart_path and os.path.exists(chart_path):
                        st.session_state.chart_path = chart_path
                        st.success("✅ Chart generated!")
                        st.rerun()
                    else:
                        st.error("Could not generate chart. Try different columns.")

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Auto-generate button ────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🤖 Auto-Generate Best Chart", width='stretch', type='secondary'):
            with st.spinner("Analyzing data and creating visualization..."):
                chart_path = make_chart(data, analysis)
                if chart_path and os.path.exists(chart_path):
                    st.session_state.chart_path = chart_path
                    st.success("✅ Best chart auto-generated!")
                    st.rerun()
                else:
                    st.error("Could not auto-generate chart")

        # ── Display chart ───────────────────────────────────────────────────
        if st.session_state.chart_path and os.path.exists(st.session_state.chart_path):
            img_b64 = get_img_as_base64(st.session_state.chart_path)
            if img_b64:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.04); border-radius: 12px; padding: 16px; margin-top: 12px;
                            border: 1px solid rgba(255,255,255,0.06);">
                    <img src="data:image/png;base64,{img_b64}" style="width: 100%; border-radius: 8px;" />
                </div>
                """, unsafe_allow_html=True)
            
            # Download button for chart
            with open(st.session_state.chart_path, "rb") as f:
                st.download_button(
                    "💾 Download Chart",
                    f,
                    file_name="chart.png",
                    mime="image/png",
                    use_container_width=True
                )
    
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
        
        # Build diverse question suggestions (mix of stats + chart questions)
        question_suggestions = []
        # Stats questions
        for c in analysis['nums'][:2]:
            question_suggestions.append((f"What is the average {c}?", '💡'))
            question_suggestions.append((f"What is the max {c}?", '💡'))
            question_suggestions.append((f"Show me the distribution of {c}", '📊'))
        for c in analysis['cats'][:2]:
            question_suggestions.append((f"Which {c} is most common?", '💡'))
        # Chart questions
        if analysis['cats'] and analysis['nums']:
            question_suggestions.append((f"Show a bar chart of {analysis['nums'][0]} by {analysis['cats'][0]}", '📊'))
            question_suggestions.append((f"Create a pie chart of {analysis['cats'][0]}", '📊'))
        if len(analysis['nums']) >= 2:
            question_suggestions.append((f"Plot a scatter chart of {analysis['nums'][1]} vs {analysis['nums'][0]}", '📊'))
            question_suggestions.append((f"Show a line chart of {analysis['nums'][1]} over {analysis['nums'][0]}", '📊'))
        if analysis['nums']:
            question_suggestions.append((f"Make a histogram of {analysis['nums'][0]}", '📊'))
        # Data questions
        question_suggestions.append(("How many rows are there?", '💡'))
        question_suggestions.append(("Are there any missing values?", '💡'))
        question_suggestions.append(("Show me all columns", '💡'))
        
        # Alternate between stats (💡) and chart (📊) questions for variety
        stats_qs = [(q, e) for q, e in question_suggestions if e == '💡']
        chart_qs = [(q, e) for q, e in question_suggestions if e == '📊']
        mixed = []
        max_len = max(len(stats_qs), len(chart_qs))
        for i in range(max_len):
            if i < len(stats_qs):
                mixed.append(stats_qs[i])
            if i < len(chart_qs):
                mixed.append(chart_qs[i])
        
        cols = st.columns(3)
        for i, (sq, emoji) in enumerate(mixed[:9]):
            with cols[i % 3]:
                if st.button(f"{emoji} {sq}", width='stretch', key=f"qs_{i}"):
                    chart_info = detect_chart_intent(sq, data)
                    if chart_info:
                        chart_result = make_custom_chart(data, chart_info['type'], chart_info['x_col'], chart_info['y_col'])
                        if chart_result and os.path.exists(chart_result):
                            st.session_state.chart_path = chart_result
                        answer = find_answer(data, sq)
                        st.session_state.question_history.append((sq, answer, chart_result))
                    else:
                        answer = find_answer(data, sq)
                        st.session_state.question_history.append((sq, answer, None))
                    st.rerun()
        
        # Question input with voice
        st.markdown("<br>", unsafe_allow_html=True)
        vcol1, vcol2, vcol3 = st.columns([6, 1, 2])
        with vcol1:
            q = st.text_input("Type your question", placeholder="e.g., What is the average price?",
                              label_visibility="collapsed", key="question_input")
        with vcol2:
            if st.button("🎤", width='stretch', type='secondary',
                         help="Tap & speak your question (words fill directly in text box)",
                         key="voice_btn"):
                st.session_state.voice_triggered = True
                st.rerun()
        with vcol3:
            ask_btn = st.button("🔍 Ask", width='stretch', type="primary")

        # Voice input — injects JS that fills the text input and clicks Ask
        if st.session_state.voice_triggered:
            voice_input_component()
            st.session_state.voice_triggered = False  # Reset so it only runs once
        
        # Handle ask button
        if ask_btn and q:
            with st.spinner("Thinking..."):
                chart_info = detect_chart_intent(q, data)
                chart_result = None
                if chart_info:
                    chart_result = make_custom_chart(data, chart_info['type'], chart_info['x_col'], chart_info['y_col'])
                    if chart_result and os.path.exists(chart_result):
                        st.session_state.chart_path = chart_result
                    answer = find_answer(data, q) + "\n\n📈 Chart generated above!"
                else:
                    answer = find_answer(data, q)
            st.session_state.question_history.append((q, answer, chart_result))
            st.rerun()
        
        # ─── Display question history ──────────────────────────────────────
        if st.session_state.question_history:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 16px;">
                <h4 style="color: white; margin: 0 0 16px;">💬 Conversation</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for item in reversed(st.session_state.question_history):
                # Unpack: support both old (q, a) and new (q, a, chart_path) formats
                if len(item) == 3:
                    question, answer, chart_path = item
                else:
                    question, answer = item
                    chart_path = None

                # Question bubble
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 8px;">
                    <div style="background: linear-gradient(135deg, #667eea, #764ba2);
                                color: white;
                                padding: 10px 16px;
                                border-radius: 18px 18px 4px 18px;
                                max-width: 80%;
                                font-size: 0.9rem;
                                word-wrap: break-word;
                                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);">
                        🤔 {question}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Answer bubble
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 20px;">
                    <div style="background: rgba(255, 255, 255, 0.08);
                                color: rgba(255,255,255,0.9);
                                padding: 10px 16px;
                                border-radius: 18px 18px 18px 4px;
                                max-width: 80%;
                                font-size: 0.9rem;
                                line-height: 1.5;
                                word-wrap: break-word;
                                border: 1px solid rgba(255, 255, 255, 0.06);">
                        {answer}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Chart display (if generated from question)
                if chart_path and os.path.exists(chart_path):
                    img_b64 = get_img_as_base64(chart_path)
                    if img_b64:
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-start; margin-bottom: 20px;">
                            <div style="background: rgba(255,255,255,0.04); border-radius: 12px; padding: 12px;
                                        border: 1px solid rgba(255,255,255,0.06); max-width: 90%;">
                                <img src="data:image/png;base64,{img_b64}" style="width: 100%; border-radius: 8px;" />
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Clear history button
            if st.button("🗑️ Clear Chat", width='stretch'):
                st.session_state.question_history = []
                st.rerun()
        