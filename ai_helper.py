"""Generate AI insights using LLM APIs."""
import requests
import pandas as pd
from config import Settings

def make_summary(analysis):
    """Build short text summary from analysis results."""
    parts = [f'Dataset: {analysis["rows"]} rows, {analysis["cols"]} cols']
    parts.append(f'Missing: {analysis["missing"]}, Duplicates: {analysis["dupes"]}')
    if analysis.get('num_stats'):
        parts.append('Numeric columns:')
        for s in analysis['num_stats']:
            parts.append(f'  {s["col"]}: mean={s["mean"]}, range=({s["min"]}-{s["max"]})')
    if analysis.get('cat_stats'):
        for s in analysis['cat_stats']:
            top = list(s['top'].items())[:3]
            parts.append(f'{s["col"]}: {s["unique"]} unique. Top: {top}')
    return '\n'.join(parts)

def make_data_sample(data, max_rows=10):
    """Build a sample of raw data rows as formatted text."""
    if data is None or len(data) == 0:
        return ''
    sample = data.head(max_rows)
    lines = [f'Sample rows ({min(max_rows, len(data))} of {len(data)}):']
    lines.append(sample.to_string(index=False))
    return '\n'.join(lines)

def get_insight(analysis, data=None):
    """Ask AI for insight. Returns text or None."""
    key = Settings.get_key()
    if not key:
        return None
    summary = make_summary(analysis)
    sample = make_data_sample(data)
    # System: role & instructions
    system = (
        'You are a data analyst. '
        'Give one key finding, one insight, and one suggestion. '
        'Be specific, reference actual values. Under 120 words.'
    )
    # User: the actual data
    user = ['Dataset Analysis:', '', summary]
    if sample:
        user.extend(['', sample])
    user = '\n'.join(user)
    try:
        if Settings.LLM_PROVIDER == 'gemini':
            return _gemini(key, system, user)
        return _openai(key, system, user)
    except Exception as e:
        print(f'AI Error: {e}')
        return None

def _openai(key, system, user):
    """Call OpenAI/Groq API."""
    resp = requests.post(
        f'{Settings.get_url()}/chat/completions',
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
        json={'model': Settings.get_model(), 'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}], 'max_tokens': Settings.MAX_TOKENS, 'temperature': Settings.TEMPERATURE},
        timeout=30
    )
    if resp.status_code == 401:
        print('ERROR: Invalid API key')
        return None
    return resp.json()['choices'][0]['message']['content']

def _gemini(key, system, user):
    """Call Gemini API."""
    url = f'{Settings.GEMINI_URL}/models/{Settings.GEMINI_MODEL}:generateContent'
    resp = requests.post(f'{url}?key={key}', json={'contents': [{'parts': [{'text': system + '\n' + user}]}]}, timeout=30)
    if resp.status_code == 403:
        print('ERROR: Invalid API key')
        return None
    return resp.json()['candidates'][0]['content']['parts'][0]['text']
