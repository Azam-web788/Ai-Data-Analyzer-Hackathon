"""Create charts from data automatically — many chart types supported."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from config import Settings

sns.set_style("darkgrid")
sns.set_palette("viridis")

CHART_TYPES = {
    'bar': '📊 Bar Chart',
    'histogram': '📈 Histogram',
    'scatter': '🔵 Scatter Plot',
    'pie': '🥧 Pie Chart',
    'box': '📦 Box Plot',
    'line': '📉 Line Chart',
    'area': '📊 Area Chart',
    'heatmap': '🔥 Correlation Heatmap',
    'violin': '🎻 Violin Plot',
    'pairplot': '🔗 Pair Plot',
}


def pick_chart(data, analysis):
    """Return up to 8 auto-detected chart suggestions.

    Each suggestion is (style, x_col, y_col, title).
    """
    nums = analysis['nums']
    cats = analysis['cats']
    suggestions = []

    if cats and nums:
        suggestions.append(('bar', cats[0], nums[0], f'{nums[0]} by {cats[0]}'))
        suggestions.append(('box', cats[0], nums[0], f'{nums[0]} Distribution by {cats[0]}'))
        suggestions.append(('violin', cats[0], nums[0], f'{nums[0]} Density by {cats[0]}'))
    if len(nums) >= 2:
        suggestions.append(('scatter', nums[0], nums[1], f'{nums[1]} vs {nums[0]}'))
        suggestions.append(('line', nums[0], nums[1], f'{nums[1]} over {nums[0]}'))
        suggestions.append(('area', nums[0], nums[1], f'{nums[1]} Area by {nums[0]}'))
    if nums:
        suggestions.append(('histogram', nums[0], None, f'Distribution of {nums[0]}'))
    if cats:
        suggestions.append(('bar', cats[0], None, f'Frequency of {cats[0]}'))
        suggestions.append(('pie', cats[0], None, f'Proportion of {cats[0]}'))
    if len(nums) >= 2:
        suggestions.append(('heatmap', None, None, 'Correlation Heatmap'))
    if len(nums) >= 1:
        suggestions.append(('pairplot', None, None, 'All Numeric Pairs'))

    return suggestions[:8]


def make_chart(data, analysis):
    """Auto mode: pick best chart and render it. Returns path or None."""
    suggestions = pick_chart(data, analysis)
    if not suggestions:
        return None
    style, x_col, y_col, title = suggestions[0]
    return render_chart(data, style, x_col, y_col, title)


def make_custom_chart(data, chart_type, x_col=None, y_col=None, title=None):
    """Render a chart with user-specified type and columns."""
    if not title:
        labels = {k: v.split(' ', 1)[1] for k, v in CHART_TYPES.items()}
        title = labels.get(chart_type, 'Chart')
    return render_chart(data, chart_type, x_col, y_col, title)


def render_chart(data, style, x_col, y_col, title, output_path=None):
    """Dispatch to the appropriate chart renderer and save PNG."""
    os.makedirs(Settings.CHART_DIR, exist_ok=True)
    if output_path is None:
        output_path = os.path.join(Settings.CHART_DIR, Settings.CHART_FILE)
    fig = None

    try:
        if style == 'bar':
            fig, ax = plt.subplots(figsize=(12, 7))
            _bar(data, ax, x_col, y_col)
        elif style == 'histogram':
            fig, ax = plt.subplots(figsize=(10, 6))
            _histogram(data, ax, x_col)
        elif style == 'scatter':
            fig, ax = plt.subplots(figsize=(10, 7))
            _scatter(data, ax, x_col, y_col)
        elif style == 'pie':
            fig, ax = plt.subplots(figsize=(10, 8))
            _pie(data, ax, x_col, y_col)
        elif style == 'box':
            fig, ax = plt.subplots(figsize=(12, 7))
            _box(data, ax, x_col, y_col)
        elif style == 'line':
            fig, ax = plt.subplots(figsize=(12, 6))
            _line(data, ax, x_col, y_col)
        elif style == 'area':
            fig, ax = plt.subplots(figsize=(12, 6))
            _area(data, ax, x_col, y_col)
        elif style == 'heatmap':
            fig, ax = plt.subplots(figsize=(10, 8))
            _heatmap(data, ax)
        elif style == 'violin':
            fig, ax = plt.subplots(figsize=(12, 7))
            _violin(data, ax, x_col, y_col)
        elif style == 'pairplot':
            return _pairplot(data, title, output_path)
        else:
            raise ValueError(f"Unknown chart type: {style}")

        # Common styling
        if fig is not None and ax is not None:
            if style != 'heatmap':
                ax.grid(True, axis='y', alpha=0.3)
            ax.set_title(title, fontsize=15, fontweight='bold', pad=15, color='#2c3e50')
            sns.despine(top=True, right=True, left=False, bottom=False)
            plt.tight_layout()

            fig.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            return output_path

    except Exception as e:
        print(f'Chart error ({style}): {e}')
        if fig is not None:
            plt.close(fig)
        return None

    return None


def generate_dashboard(data, analysis, count=None):
    """Generate a grid of multiple charts for dashboard view.

    Picks the top `count` suggestions from pick_chart() and renders each
    as a separate PNG. Cleans up old dashboard PNGs first.
    Returns list of (title, file_path) tuples.
    """
    if count is None:
        count = Settings.DASHBOARD_COUNT

    suggestions = pick_chart(data, analysis)
    if not suggestions:
        return []

    os.makedirs(Settings.CHART_DIR, exist_ok=True)

    # Clean up old dashboard PNGs
    for f in os.listdir(Settings.CHART_DIR):
        if f.startswith(Settings.DASHBOARD_PREFIX) and f.endswith('.png'):
            try:
                os.remove(os.path.join(Settings.CHART_DIR, f))
            except OSError:
                pass

    results = []
    for i, (style, x_col, y_col, title) in enumerate(suggestions[:count]):
        fname = f"{Settings.DASHBOARD_PREFIX}{i}.png"
        fpath = os.path.join(Settings.CHART_DIR, fname)
        path = render_chart(data, style, x_col, y_col, title, output_path=fpath)
        if path and os.path.exists(path):
            results.append((title, path))

    return results


# ── Individual Chart Renderers ──────────────────────────────────────────────


def _bar(data, ax, x_col, y_col):
    """Bar chart – grouped mean or frequency."""
    if y_col:
        plot_data = data.groupby(x_col)[y_col].mean().sort_values(ascending=False).head(15)
        ylabel = f'Average {y_col}'
    else:
        plot_data = data[x_col].value_counts().head(15)
        ylabel = 'Count'

    colors = plt.cm.viridis(np.linspace(0, 0.85, len(plot_data)))
    bars = ax.bar(range(len(plot_data)), plot_data.values, color=colors, edgecolor='white', linewidth=0.6)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_xlabel(x_col, fontsize=11)
    ax.set_xticks(range(len(plot_data)))
    ax.set_xticklabels(plot_data.index, rotation=45, ha='right', fontsize=9)

    # Value labels on bars
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + h * 0.02,
                f'{h:.1f}' if h >= 10 else f'{h:.2f}',
                ha='center', va='bottom', fontsize=8, fontweight='bold', color='#555')


def _histogram(data, ax, x_col):
    """Histogram with KDE overlay."""
    v = data[x_col].dropna()
    ax.hist(v, bins=25, color='#667eea', edgecolor='white', alpha=0.7, density=True)
    # KDE overlay
    try:
        sns.kdeplot(v, ax=ax, color='#e74c3c', linewidth=2, label='Density')
        ax.legend(fontsize=9)
    except Exception:
        pass
    ax.set_xlabel(x_col, fontsize=11)
    ax.set_ylabel('Density', fontsize=11)

    # Stats annotation
    stats_text = f'μ={v.mean():.2f}\nσ={v.std():.2f}\nn={len(v):,}'
    ax.text(0.95, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8))


def _scatter(data, ax, x_col, y_col):
    """Scatter plot with regression line."""
    v = data[[x_col, y_col]].dropna()
    ax.scatter(v[x_col], v[y_col], alpha=0.6, s=30, c='#667eea',
               edgecolors='white', linewidth=0.5, zorder=3)
    # Regression line
    try:
        sns.regplot(data=v, x=x_col, y=y_col, ax=ax, scatter=False,
                     line_kws={'color': '#e74c3c', 'linewidth': 2, 'linestyle': '--'})
    except Exception:
        pass
    ax.set_xlabel(x_col, fontsize=11)
    ax.set_ylabel(y_col, fontsize=11)

    # Correlation annotation
    corr = v[x_col].corr(v[y_col])
    ax.text(0.05, 0.95, f'r = {corr:.3f}', transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))


def _pie(data, ax, x_col, y_col):
    """Pie chart – proportion of categories."""
    if y_col:
        g = data.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(10)
    else:
        g = data[x_col].value_counts().head(10)

    colors = plt.cm.viridis(np.linspace(0, 0.85, len(g)))
    wedges, texts, autotexts = ax.pie(
        g.values, labels=None, autopct='%1.1f%%',
        colors=colors, startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
        textprops={'fontsize': 9, 'fontweight': 'bold'}
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontsize(8)

    # Legend
    labels = [f'{k}  ({v:,.0f})' for k, v in g.items()]
    ax.legend(wedges, labels, title=x_col, loc='center left',
              bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9, title_fontsize=10)
    ax.set_ylabel('')


def _box(data, ax, x_col, y_col):
    """Box plot – numeric distribution across categories."""
    v = data[[x_col, y_col]].dropna()
    order = v.groupby(x_col)[y_col].median().sort_values(ascending=False).index[:12]
    sns.boxplot(data=v, x=x_col, y=y_col, order=order, ax=ax,
                palette='viridis', linewidth=1.2, fliersize=4)
    ax.set_xlabel(x_col, fontsize=11)
    ax.set_ylabel(y_col, fontsize=11)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)


def _line(data, ax, x_col, y_col):
    """Line chart – trend across ordered x."""
    v = data[[x_col, y_col]].dropna().sort_values(x_col)
    ax.plot(v[x_col], v[y_col], color='#667eea', linewidth=2, marker='o',
            markersize=4, markerfacecolor='white', markeredgecolor='#667eea',
            markeredgewidth=1.5, zorder=3)
    ax.fill_between(v[x_col], v[y_col], alpha=0.08, color='#667eea')
    ax.set_xlabel(x_col, fontsize=11)
    ax.set_ylabel(y_col, fontsize=11)
    # Rotate x labels if many unique values
    if len(v) > 10:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)


def _area(data, ax, x_col, y_col):
    """Area chart – filled line chart."""
    v = data[[x_col, y_col]].dropna().sort_values(x_col)
    ax.fill_between(v[x_col], v[y_col], alpha=0.4, color='#667eea')
    ax.plot(v[x_col], v[y_col], color='#667eea', linewidth=2, zorder=3)
    ax.set_xlabel(x_col, fontsize=11)
    ax.set_ylabel(y_col, fontsize=11)
    if len(v) > 10:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)


def _heatmap(data, ax):
    """Correlation heatmap for numeric columns."""
    nums = data.select_dtypes(include=[np.number]).columns.tolist()
    if len(nums) < 2:
        ax.text(0.5, 0.5, 'Need at least 2 numeric columns', ha='center', va='center')
        return
    corr = data[nums].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, vmin=-1, vmax=1, square=True, linewidths=1,
                cbar_kws={'shrink': 0.8}, ax=ax)
    ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)


def _violin(data, ax, x_col, y_col):
    """Violin plot – distribution density across categories."""
    v = data[[x_col, y_col]].dropna()
    order = v.groupby(x_col)[y_col].median().sort_values(ascending=False).index[:10]
    sns.violinplot(data=v, x=x_col, y=y_col, order=order, ax=ax,
                   palette='viridis', inner='quartile', linewidth=1.2)
    ax.set_xlabel(x_col, fontsize=11)
    ax.set_ylabel(y_col, fontsize=11)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)


def _pairplot(data, title, output_path=None):
    """Pair plot – scatter matrix of all numeric columns. Saves separately."""
    nums = data.select_dtypes(include=[np.number]).columns.tolist()
    if len(nums) < 2:
        return None
    if len(nums) > 6:
        nums = nums[:6]  # Limit to 6 for readability
    if output_path is None:
        output_path = os.path.join(Settings.CHART_DIR, Settings.CHART_FILE)

    g = sns.pairplot(data[nums].dropna(), diag_kind='kde', palette='viridis',
                     plot_kws={'alpha': 0.6, 's': 25, 'edgecolor': 'white', 'linewidth': 0.5},
                     diag_kws={'color': '#667eea'})
    g.fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)

    g.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(g.fig)
    return output_path
