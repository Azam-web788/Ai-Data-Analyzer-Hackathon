"""Answer plain English questions about datasets."""
import pandas as pd

def find_answer(data, question):
    """Parse question and return answer string."""
    q = question.lower().strip()
    cols = {c.lower(): c for c in data.columns}
    target = None
    for low, orig in cols.items():
        if low in q:
            target = orig
            break
    if any(w in q for w in ['max', 'highest', 'largest']):
        return _max(data, target)
    if any(w in q for w in ['min', 'lowest', 'smallest']):
        return _min(data, target)
    if any(w in q for w in ['average', 'mean']):
        return _avg(data, target)
    if any(w in q for w in ['sum', 'total']):
        return _sum(data, target)
    if any(w in q for w in ['count', 'how many']):
        return _cnt(data, target, q)
    if any(w in q for w in ['most common', 'frequent', 'popular', 'appears most']):
        return _freq(data, target)
    return _suggest(data)

def _max(data, col):
    if not col:
        for c in data.columns:
            if pd.api.types.is_numeric_dtype(data[c]):
                col = c; break
    if col and pd.api.types.is_numeric_dtype(data[col]):
        return f'Highest {col}: {data[col].max()}'
    return 'Could not find a numeric column'

def _min(data, col):
    if not col:
        for c in data.columns:
            if pd.api.types.is_numeric_dtype(data[c]):
                col = c; break
    if col and pd.api.types.is_numeric_dtype(data[col]):
        return f'Lowest {col}: {data[col].min()}'
    return 'Could not find a numeric column'

def _avg(data, col):
    if not col:
        for c in data.columns:
            if pd.api.types.is_numeric_dtype(data[c]):
                col = c; break
    if col and pd.api.types.is_numeric_dtype(data[col]):
        return f'Average {col}: {data[col].mean():.2f}'
    return 'Could not find a numeric column'

def _sum(data, col):
    if not col:
        for c in data.columns:
            if pd.api.types.is_numeric_dtype(data[c]):
                col = c; break
    if col and pd.api.types.is_numeric_dtype(data[col]):
        return f'Total {col}: {data[col].sum():,.2f}'
    return 'Could not find a numeric column'

def _cnt(data, col, q):
    if 'unique' in q or 'distinct' in q:
        if col:
            return f'{col}: {data[col].nunique()} unique values'
        return f'{len(data.drop_duplicates())} unique records'
    if col:
        return f'{col}: {data[col].count()} values'
    return f'{len(data)} rows, {len(data.columns)} columns'

def _freq(data, col):
    if not col:
        for c in data.columns:
            if not pd.api.types.is_numeric_dtype(data[c]):
                col = c; break
    if col:
        vc = data[col].value_counts()
        top = vc.index[0]
        pct = (vc.iloc[0] / vc.sum()) * 100
        return f'Most common {col}: {top} ({vc.iloc[0]} times, {pct:.1f}%)'
    return 'Could not find a text column'

def _suggest(data):
    """Suggest questions based on column names."""
    tips = []
    for c in data.columns[:3]:
        if pd.api.types.is_numeric_dtype(data[c]):
            tips.append(f'What is the average {c}?')
        else:
            tips.append(f'Which {c} is most common?')
    return 'Try: ' + ' | '.join(tips[:4])
