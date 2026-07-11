"""Analyze datasets: detect types, calculate statistics."""
import pandas as pd
import warnings

def detect_types(data):
    """Categorize columns as numeric, categorical, or date."""
    nums, cats, dates = [], [], []
    for col in data.columns:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                parsed = pd.to_datetime(data[col], errors='coerce')
            if parsed.notna().sum() > len(data) * 0.5:
                dates.append(col)
                continue
        except:
            pass
        if pd.api.types.is_numeric_dtype(data[col]) and not pd.api.types.is_bool_dtype(data[col]):
            nums.append(col)
        else:
            cats.append(col)
    return nums, cats, dates

def analyze_num(data, col):
    """Statistics for a numeric column."""
    v = data[col].dropna()
    if len(v) == 0:
        return {'col': col, 'count': 0, 'mean': 0, 'median': 0, 'max': 0, 'min': 0}
    # Convert to float first to handle numpy.bool_, numpy.int64, etc.
    mean_val = round(float(v.mean()), 2)
    median_val = round(float(v.median()), 2)
    max_val = round(float(v.max()), 2)
    min_val = round(float(v.min()), 2)
    return {'col': col, 'count': len(v), 'mean': mean_val, 'median': median_val, 'max': max_val, 'min': min_val}

def analyze_cat(data, col):
    """Statistics for a categorical column."""
    v = data[col].dropna()
    top = v.value_counts().head(5).to_dict()
    return {'col': col, 'count': len(v), 'unique': v.nunique(), 'top': top}

def run_full_analysis(data):
    """Complete analysis of the dataset."""
    nums, cats, dates = detect_types(data)
    result = {
        'rows': len(data), 'cols': len(data.columns),
        'nums': nums, 'cats': cats, 'dates': dates,
        'missing': int(data.isnull().sum().sum()),
        'dupes': int(data.duplicated().sum()),
        'num_stats': [analyze_num(data, c) for c in nums],
        'cat_stats': [analyze_cat(data, c) for c in cats]
    }
    if len(nums) >= 2:
        result['corr'] = data[nums].corr()
    return result
