"""Create charts from data automatically."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import Settings

def pick_chart(data, analysis):
    """Choose best chart type based on data."""
    nums = analysis['nums']
    cats = analysis['cats']
    if cats and nums:
        return 'bar', cats[0], nums[0], f'{nums[0]} by {cats[0]}'
    if len(nums) >= 2:
        return 'scatter', nums[0], nums[1], f'{nums[1]} vs {nums[0]}'
    if len(nums) == 1:
        return 'histogram', nums[0], None, f'Distribution of {nums[0]}'
    if cats:
        return 'bar', cats[0], None, f'Frequency of {cats[0]}'
    return 'bar', data.columns[0], None, data.columns[0]

def make_chart(data, analysis):
    """Create and save chart PNG. Returns file path or None."""
    os.makedirs(Settings.CHART_DIR, exist_ok=True)
    style, x_col, y_col, title = pick_chart(data, analysis)
    fig, ax = plt.subplots(figsize=(10, 6))
    try:
        if style == 'bar':
            if y_col:
                g = data.groupby(x_col)[y_col].mean().sort_values(ascending=False)
                ax.bar(range(len(g)), g.values, color=plt.cm.viridis(range(len(g))))
                ax.set_xticks(range(len(g)))
                ax.set_xticklabels(g.index, rotation=45, ha='right')
                ax.set_ylabel(f'Average {y_col}')
            else:
                f = data[x_col].value_counts().head(10)
                ax.bar(range(len(f)), f.values, color=plt.cm.viridis(range(len(f))))
                ax.set_xticks(range(len(f)))
                ax.set_xticklabels(f.index, rotation=45, ha='right')
                ax.set_ylabel('Count')
            ax.set_xlabel(x_col)
        elif style == 'histogram':
            ax.hist(data[x_col].dropna(), bins=20, color='steelblue', edgecolor='white')
            ax.set_xlabel(x_col)
            ax.set_ylabel('Frequency')
        elif style == 'scatter':
            ax.scatter(data[x_col], data[y_col], alpha=0.6, color='steelblue', edgecolors='white')
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        path = os.path.join(Settings.CHART_DIR, Settings.CHART_FILE)
        fig.savefig(path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return path
    except Exception as e:
        print(f'Chart error: {e}')
        plt.close(fig)
        return None
