"""Configuration module: lightweight settings, no external API dependencies."""

import os


class Settings:
    """Central place for all app configuration (local-only, no API keys)."""
    
    # Chart output
    CHART_DIR = 'charts'
    CHART_FILE = 'output_chart.png'

    # Dashboard grid
    DASHBOARD_PREFIX = 'dashboard_'
    DASHBOARD_COUNT = 4
