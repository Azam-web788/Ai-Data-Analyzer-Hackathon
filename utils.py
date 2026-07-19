"""Answer natural language questions about datasets - supports English, Urdu & Hindi."""
import pandas as pd
import re

# ─── Urdu/Hindi keyword mappings ───────────────────────────────────────────────────
_KEYWORDS = {
    'max': [
        'max', 'maximum', 'highest', 'largest', 'biggest', 'most expensive',
        'sabse bada', 'sabse bara', 'sabse zyada', 'sab se zyada', 'zyada se zyada',
        'अधिकतम', 'सबसे बड़ा', 'सबसे बड़ी', 'सबसे बड़े', 'सबसे ज्यादा',
    ],
    'min': [
        'min', 'minimum', 'lowest', 'smallest', 'least', 'cheapest',
        'sabse chhota', 'sabse chota', 'sabse kam', 'sab se kam',
        'न्यूनतम', 'सबसे छोटा', 'सबसे छोटी', 'सबसे छोटे', 'सबसे कम',
    ],
    'avg': [
        'average', 'mean', 'avg',
        'ausat', 'osat',
        'औसत', 'माध्य',
    ],
    'median': [
        'median', 'middle',
        'darmiyan', 'darmiani',
        'माध्यिका', 'बीच',
    ],
    'sum': [
        'sum', 'total', 'all',
        'kul', 'jama', 'jod', 'jor',
        'कुल', 'जोड़', 'योग', 'जमा',
    ],
    'count': [
        'count', 'how many', 'number of',
        'kitne', 'kitna', 'ginati', 'ginti',
        'कितने', 'कितना', 'गिनती', 'संख्या',
    ],
    'freq': [
        'most common', 'frequent', 'popular', 'appears most', 'mode',
        'sabse aam', 'sabse zyada baar',
        'सबसे आम', 'सबसे अधिक बार', 'बहुलक',
    ],
    'unique': [
        'unique', 'distinct', 'different',
        'mukhtalif', 'alag alag', 'alag-alag',
        'अद्वितीय', 'भिन्न', 'अलग अलग',
    ],
    'range': [
        'range', 'spread', 'difference between min',
        'fail', 'phase',
        'श्रेणी', 'सीमा', 'अंतर',
    ],
    'std': [
        'deviation', 'standard dev', 'variance',
        'infiraq', 'inkishaf',
        'विचलन', 'मानक विचलन', 'प्रसरण',
    ],
    'compare': [
        'compare', 'versus', 'vs', 'difference between',
        'muqabla', 'farq', 'taqabul',
        'तुलना', 'अंतर', 'बनाम',
    ],
    'top': [
        'top', 'highest rated', 'best',
        'behtareen', 'sabse acha', 'top',
        'शीर्ष', 'सर्वश्रेष्ठ', 'सबसे अच्छा',
    ],
    'bottom': [
        'bottom', 'lowest rated', 'worst', 'last',
        'sabse bura', 'sabse kharab',
        'निचला', 'सबसे खराब', 'अंतिम',
    ],
    'chart': [
        'chart', 'graph', 'plot', 'visualize', 'show me', 'draw',
        'bar chart', 'pie chart', 'histogram', 'scatter plot',
        'line chart', 'box plot', 'area chart', 'heatmap', 'violin',
        'distribution of', 'correlation between',
        'chart banao', 'graph banao', 'plot banao',
        'चार्ट', 'ग्राफ', 'प्लॉट', 'दिखाओ',
    ],
}

# ─── Column name aliases (English → Urdu/Hindi) ────────────────────────────────────
_COLUMN_ALIASES = {
    'price': ['price', 'qemat', 'qimat', 'daam', 'kimat', 'मूल्य', 'कीमत', 'दाम', 'rate'],
    'quantity': ['quantity', 'qty', 'miqdar', 'tadaad', 'tadad', 'मात्रा', 'संख्या', 'तादाद'],
    'rating': ['rating', 'ratings', 'review', 'score', 'darja', 'darajat', 'रेटिंग', 'दर्जा', 'रिव्यू'],
    'category': ['category', 'categories', 'cat', 'qism', 'zumra', 'श्रेणी', 'कैटेगरी', 'प्रकार', 'किस्म'],
    'product': ['product', 'item', 'name', 'product name', 'cheez', 'saman', 'उत्पाद', 'वस्तु', 'चीज़', 'सामान'],
    'city': ['city', 'cities', 'town', 'location', 'shehar', 'shahar', 'शहर', 'स्थान', 'नगर'],
    'date': ['date', 'dates', 'day', 'time', 'sales date', 'tareekh', 'तारीख', 'दिनांक', 'दिन'],
    'count': ['count', 'frequency', 'freq',
    ],
}


def _find_column(data, question):
    """Find the best matching column for a question.
    Returns (column_name, is_numeric) or (None, None)."""
    q = question.lower().strip()
    
    # 1. Try exact column name match (handles spaces -> underscores)
    for col in data.columns:
        col_lower = col.lower().replace('_', ' ').replace('-', ' ')
        if col_lower in q:
            return col, pd.api.types.is_numeric_dtype(data[col])
    
    # 2. Try plural/singular variants
    for col in data.columns:
        col_lower = col.lower().replace('_', ' ').replace('-', ' ')
        # Check if column starts/ends with words in the question
        words = q.split()
        for w in words:
            if len(w) >= 3 and (col_lower.startswith(w) or w.startswith(col_lower) or
                                col_lower.endswith(w) or w.endswith(col_lower)):
                return col, pd.api.types.is_numeric_dtype(data[col])
    
    # 3. Try alias matching
    for col in data.columns:
        col_lower = col.lower()
        for alias_list in _COLUMN_ALIASES.values():
            for alias in alias_list:
                if col_lower == alias or alias in col_lower or col_lower in alias:
                    if alias in q:
                        return col, pd.api.types.is_numeric_dtype(data[col])
        # Check if any alias word appears in both column name and question
    
    # 4. Check if question contains a column word directly
    for col in data.columns:
        col_lower = col.lower()
        col_words = set(col_lower.replace('_', ' ').replace('-', ' ').split())
        q_words = set(q.split())
        common = col_words & q_words
        if common:
            return col, pd.api.types.is_numeric_dtype(data[col])
    
    return None, None


def _detect_intent(q):
    """Detect question intent from keywords.
    Returns (intent_key, matched_keyword)."""
    for intent, keywords in _KEYWORDS.items():
        for kw in keywords:
            if kw in q:
                return intent, kw
    return None, None


def find_answer(data, question):
    """Parse question in English, Urdu, or Hindi and return answer string."""
    q = question.lower().strip()
    if not q:
        return _suggest(data)
    
    # Find matching column
    col, is_num = _find_column(data, question)
    
    # Detect intent
    intent, matched_kw = _detect_intent(q)
    
    if intent == 'max':
        return _max(data, col)
    elif intent == 'min':
        return _min(data, col)
    elif intent == 'avg':
        return _avg(data, col)
    elif intent == 'median':
        return _median(data, col)
    elif intent == 'sum':
        return _sum(data, col)
    elif intent == 'count':
        return _cnt(data, col, q)
    elif intent == 'freq':
        return _freq(data, col)
    elif intent == 'unique':
        return _unique(data, col)
    elif intent == 'range':
        return _range(data, col)
    elif intent == 'std':
        return _std(data, col)
    elif intent == 'compare':
        return _compare(data, col, q)
    elif intent == 'top':
        return _top(data, col, q)
    elif intent == 'bottom':
        return _bottom(data, col, q)
    
    # ─── General / No intent matched ────────────────────────────────────
    # Check for generic data questions
    if any(w in q for w in ['row', 'rows', 'record', 'records', 'data points', 'data point']):
        return f"📊 Dataset has **{len(data):,} rows** and **{len(data.columns)} columns**."
    
    if any(w in q for w in ['column', 'columns', 'feature', 'features', 'attribute', 'attributes']):
        cols_list = ', '.join([f'**{c}**' for c in data.columns[:8]])
        if len(data.columns) > 8:
            cols_list += f' and {len(data.columns) - 8} more'
        return f"📋 Columns: {cols_list}"
    
    if any(w in q for w in ['missing', 'null', 'empty', 'na', 'khali', 'خالی', 'खाली']):
        missing = data.isnull().sum().sum()
        if missing == 0:
            return "✅ **No missing values!** The dataset is clean."
        missing_cols = data.isnull().sum()
        missing_cols = missing_cols[missing_cols > 0].sort_values(ascending=False)
        details = ', '.join([f'**{c}**: {v}' for c, v in missing_cols.items()])
        return f"⚠️ **{missing:,}** missing values found. {details}"
    
    if any(w in q for w in ['help', 'kya', 'kiya', 'क्या', 'sakta', 'sakte', 'सकता', 'सकते']):
        return _help(data)
    
    # If a column was found but no specific intent, show its info
    if col:
        if is_num:
            v = data[col].dropna()
            return (
                f"📊 **{col}** (numeric)\n"
                f"  • Count: {len(v):,}\n"
                f"  • Mean: {v.mean():.2f}\n"
                f"  • Median: {v.median():.2f}\n"
                f"  • Min: {v.min():.2f}  |  Max: {v.max():.2f}\n"
                f"  • Std Dev: {v.std():.2f}\n"
                f"  • Sum: {v.sum():,.2f}"
            )
        else:
            vc = data[col].value_counts()
            top = vc.index[0]
            pct = (vc.iloc[0] / vc.sum()) * 100
            return (
                f"🏷️ **{col}** (categorical)\n"
                f"  • Total: {len(vc):,} unique values\n"
                f"  • Most common: **{top}** ({vc.iloc[0]:,}, {pct:.1f}%)\n"
                f"  • Least common: **{vc.index[-1]}** ({vc.iloc[-1]:,})"
            )
    
    return _suggest(data)


# ─── Intent Handlers ───────────────────────────────────────────────────────────────

def _get_num_col(data, col):
    """Get first numeric column if col is None."""
    if col and pd.api.types.is_numeric_dtype(data[col]):
        return col
    for c in data.columns:
        if pd.api.types.is_numeric_dtype(data[c]):
            return c
    return None


def _get_cat_col(data, col):
    """Get first categorical column if col is None."""
    if col and not pd.api.types.is_numeric_dtype(data[col]):
        return col
    for c in data.columns:
        if not pd.api.types.is_numeric_dtype(data[c]):
            return c
    return None


def _max(data, col):
    c = _get_num_col(data, col)
    if c:
        val = data[c].max()
        val_str = f"{val:,.2f}" if isinstance(val, float) else str(val)
        return f"📈 Highest **{c}**: **{val_str}**"
    return "❌ No numeric columns found for this query."


def _min(data, col):
    c = _get_num_col(data, col)
    if c:
        val = data[c].min()
        val_str = f"{val:,.2f}" if isinstance(val, float) else str(val)
        return f"📉 Lowest **{c}**: **{val_str}**"
    return "❌ No numeric columns found for this query."


def _avg(data, col):
    c = _get_num_col(data, col)
    if c:
        val = data[c].mean()
        return f"📊 Average **{c}**: **{val:,.2f}**"
    return "❌ No numeric columns found for this query."


def _median(data, col):
    c = _get_num_col(data, col)
    if c:
        val = data[c].median()
        return f"📊 Median **{c}**: **{val:,.2f}**"
    return "❌ No numeric columns found for this query."


def _sum(data, col):
    c = _get_num_col(data, col)
    if c:
        val = data[c].sum()
        return f"💰 Total **{c}**: **{val:,.2f}**"
    return "❌ No numeric columns found for this query."


def _cnt(data, col, q):
    if 'unique' in q or 'distinct' in q:
        if col:
            return f"🔢 **{col}**: **{data[col].nunique():,}** unique values"
        return f"🔢 Dataset has **{data.drop_duplicates().shape[0]:,}** unique records"
    if col:
        return f"🔢 **{col}**: **{data[col].count():,}** values"
    return f"🔢 Dataset has **{len(data):,}** rows and **{len(data.columns)}** columns"


def _freq(data, col):
    c = _get_cat_col(data, col)
    if c:
        vc = data[c].value_counts()
        top = vc.index[0]
        pct = (vc.iloc[0] / vc.sum()) * 100
        return f"🏆 Most common **{c}**: **{top}** ({vc.iloc[0]:,} times, {pct:.1f}%)"
    return "❌ No categorical columns found for this query."


def _unique(data, col):
    if col:
        return f"🔢 **{col}**: **{data[col].nunique():,}** unique values"
    return f"🔢 Dataset has **{len(data.columns)}** columns in total"


def _range(data, col):
    c = _get_num_col(data, col)
    if c:
        v = data[c].dropna()
        rng = v.max() - v.min()
        return f"📊 Range of **{c}**: **{v.min():,.2f}** to **{v.max():,.2f}** (Spread: **{rng:,.2f}**)"
    return "❌ No numeric columns found for this query."


def _std(data, col):
    c = _get_num_col(data, col)
    if c:
        v = data[c].dropna()
        return f"📊 **{c}**: Std Dev = **{v.std():.2f}**, Variance = **{v.var():.2f}**"
    return "❌ No numeric columns found for this query."


def _compare(data, col, q):
    # Find two numeric columns mentioned
    nums = [c for c in data.columns if pd.api.types.is_numeric_dtype(data[c])]
    mentioned = []
    for c in nums:
        c_lower = c.lower()
        if c_lower in q or c_lower.replace('_', ' ') in q:
            mentioned.append(c)
    if len(mentioned) >= 2:
        a, b = mentioned[0], mentioned[1]
        corr = data[a].corr(data[b])
        return (
            f"📊 **{a}** vs **{b}**\n"
            f"  • {a}: mean={data[a].mean():.2f}, total={data[a].sum():,.2f}\n"
            f"  • {b}: mean={data[b].mean():.2f}, total={data[b].sum():,.2f}\n"
            f"  • Correlation: **{corr:.3f}**"
        )
    if len(nums) >= 2:
        a, b = nums[0], nums[1]
        corr = data[a].corr(data[b])
        return (
            f"📊 **{a}** vs **{b}**\n"
            f"  • {a}: mean={data[a].mean():.2f}, total={data[a].sum():,.2f}\n"
            f"  • {b}: mean={data[b].mean():.2f}, total={data[b].sum():,.2f}\n"
            f"  • Correlation: **{corr:.3f}**"
        )
    return "❌ Need at least 2 numeric columns to compare."


def _top(data, col, q):
    """Show top N items. Default 5."""
    # Extract number if present
    nums_in_q = re.findall(r'\d+', q)
    n = int(nums_in_q[0]) if nums_in_q else 5
    n = min(n, 20)
    
    if col and pd.api.types.is_numeric_dtype(data[col]):
        result = data.nlargest(n, col)
        vals = [f"**{i+1}.** {r[col]:,.2f}" for i, (_, r) in enumerate(result.iterrows())]
        return f"🏆 Top **{n}** **{col}** values:\n" + '\n'.join(vals)
    
    # Categorical: show most frequent
    c = _get_cat_col(data, col)
    if c:
        vc = data[c].value_counts().head(n)
        vals = [f"**{i+1}.** {k} ({v:,})" for i, (k, v) in enumerate(vc.items())]
        return f"🏆 Top **{n}** **{c}**:\n" + '\n'.join(vals)
    return "❌ Could not process this query."


def _bottom(data, col, q):
    nums_in_q = re.findall(r'\d+', q)
    n = int(nums_in_q[0]) if nums_in_q else 5
    n = min(n, 20)
    
    if col and pd.api.types.is_numeric_dtype(data[col]):
        result = data.nsmallest(n, col)
        vals = [f"**{i+1}.** {r[col]:,.2f}" for i, (_, r) in enumerate(result.iterrows())]
        return f"📉 Bottom **{n}** **{col}** values:\n" + '\n'.join(vals)
    
    c = _get_cat_col(data, col)
    if c:
        vc = data[c].value_counts().tail(n).sort_values(ascending=True)
        vals = [f"**{i+1}.** {k} ({v:,})" for i, (k, v) in enumerate(vc.items())]
        return f"📉 Bottom **{n}** **{c}**:\n" + '\n'.join(vals)
    return "❌ Could not process this query."


def _help(data):
    """Show help with examples."""
    examples = []
    for c in data.columns[:2]:
        if pd.api.types.is_numeric_dtype(data[c]):
            examples.append(f'  • "What is the average {c}?"')
            examples.append(f'  • "Max {c} kya hai?"')
            examples.append(f'  • "{c} ka ausat kya hai?"')
            examples.append(f'  • "{c} ka औसत क्या है?"')
        else:
            examples.append(f'  • "Which {c} is most common?"')
            examples.append(f'  • "{c} sabse aam kya hai?"')
    
    return (
        "💡 **Try asking:**\n"
        + '\n'.join(examples[:6])
        + "\n\n🌐 Works in **English**, **Urdu**, and **Hindi**!"
    )


def _suggest(data):
    """Suggest questions based on column names."""
    tips = []
    for c in data.columns[:4]:
        if pd.api.types.is_numeric_dtype(data[c]):
            tips.append(f'📊 Average **{c}**')
            tips.append(f'📈 Max **{c}**')
        else:
            tips.append(f'🏷️ Most common **{c}**')
    return (
        "🤔 I didn't understand that question. Try:\n"
        + '\n'.join(tips[:6])
        + "\n\n💡 Or type **'help'** for examples in English, Urdu & Hindi!"
    )


def detect_chart_intent(question, data):
    """Detect if a question is asking for a chart and determine chart params.

    Returns dict with 'type', 'x_col', 'y_col' keys, or None if no chart intent.
    """
    q = question.lower().strip()

    # Detect chart type keywords
    nums = [c for c in data.columns if pd.api.types.is_numeric_dtype(data[c])]
    cats = [c for c in data.columns if not pd.api.types.is_numeric_dtype(data[c])]

    chart_type = None
    x_col = None
    y_col = None

    # Check which chart type is mentioned
    if any(w in q for w in ['bar', 'bar chart', 'bar graph']):
        chart_type = 'bar'
    elif any(w in q for w in ['pie', 'pie chart']):
        chart_type = 'pie'
    elif any(w in q for w in ['histogram', 'distribution']):
        chart_type = 'histogram'
    elif any(w in q for w in ['scatter', 'scatter plot', 'correlation between']):
        chart_type = 'scatter'
    elif any(w in q for w in ['line', 'line chart', 'trend', 'over time']):
        chart_type = 'line'
    elif any(w in q for w in ['box', 'box plot']):
        chart_type = 'box'
    elif any(w in q for w in ['area', 'area chart']):
        chart_type = 'area'
    elif any(w in q for w in ['heatmap', 'correlation heatmap']):
        chart_type = 'heatmap'
    elif any(w in q for w in ['violin', 'violin plot']):
        chart_type = 'violin'

    # If chart type detected, find columns
    if chart_type:
        # Find x column (categorical for bar/pie/box/violin, numeric for histogram/scatter/line/area)
        if chart_type in ('bar', 'pie', 'box', 'violin'):
            # Try to find a categorical column mentioned first
            for c in cats:
                c_lower = c.lower().replace('_', ' ').replace('-', ' ')
                if c_lower in q:
                    x_col = c
                    break
            if not x_col and cats:
                x_col = cats[0]
            # Try to find a numeric column mentioned for y
            for c in nums:
                c_lower = c.lower().replace('_', ' ').replace('-', ' ')
                if c_lower in q:
                    y_col = c
                    break
            if not y_col and nums:
                y_col = nums[0]
        elif chart_type == 'histogram':
            for c in nums:
                c_lower = c.lower().replace('_', ' ').replace('-', ' ')
                if c_lower in q:
                    x_col = c
                    break
            if not x_col and nums:
                x_col = nums[0]
        else:  # scatter, line, area
            for c in nums:
                c_lower = c.lower().replace('_', ' ').replace('-', ' ')
                if c_lower in q:
                    if x_col is None:
                        x_col = c
                    elif y_col is None:
                        y_col = c
            if not x_col and len(nums) >= 1:
                x_col = nums[0]
            if not y_col and len(nums) >= 2:
                y_col = nums[1]

        return {'type': chart_type, 'x_col': x_col, 'y_col': y_col}

    # Generic chart request (no specific type) — auto-pick
    if any(w in q for w in ['chart', 'graph', 'plot', 'visualize', 'show me', 'draw',
                             'chart banao', 'graph banao', 'plot banao',
                             'चार्ट', 'ग्राफ', 'प्लॉट', 'दिखाओ']):
        # Auto-detect: prefer bar if cats+nums, else scatter, else histogram
        if cats and nums:
            chart_type = 'bar'
            x_col = cats[0]
            y_col = nums[0]
        elif len(nums) >= 2:
            chart_type = 'scatter'
            x_col = nums[0]
            y_col = nums[1]
        elif nums:
            chart_type = 'histogram'
            x_col = nums[0]
        elif cats:
            chart_type = 'bar'
            x_col = cats[0]
        else:
            return None

        return {'type': chart_type, 'x_col': x_col, 'y_col': y_col}

    return None
