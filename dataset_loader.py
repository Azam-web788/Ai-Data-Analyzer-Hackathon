"""Load CSV / Excel files safely with encoding detection."""
import pandas as pd
import os

def load_csv(path):
    """Read CSV from path, return DataFrame or None on error."""
    if not os.path.exists(path):
        print(f'ERROR: File not found: {path}')
        return None
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            data = pd.read_csv(path, encoding=enc)
            if data.empty:
                print('ERROR: Empty CSV')
                return None
            return data
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f'ERROR: {e}')
            return None
    print('ERROR: Could not decode file')
    return None

def load_excel(path):
    """Read Excel (.xlsx / .xls) from path, return DataFrame or None on error."""
    if not os.path.exists(path):
        print(f'ERROR: File not found: {path}')
        return None
    try:
        data = pd.read_excel(path)
        if data.empty:
            print('ERROR: Empty Excel file')
            return None
        return data
    except Exception as e:
        print(f'ERROR: {e}')
        return None

def show_info(data):
    """Print dataset summary."""
    print(f'Rows: {len(data):,}  Columns: {len(data.columns)}')
    print(f'Missing: {data.isnull().sum().sum()}  Duplicates: {data.duplicated().sum()}')
    for col, dtype in data.dtypes.items():
        print(f'  {col}: {dtype}')
