"""Generate data insights locally using pandas statistics (no external APIs)."""


def get_insight(analysis, data=None):
    """Generate comprehensive local insights from data analysis.
    
    Returns a formatted string with findings, patterns, and suggestions
    derived purely from pandas statistics.
    """
    parts = []
    
    # ─── 1. Dataset Overview ────────────────────────────────────────────
    parts.append("📊 **Dataset Overview**")
    parts.append(f"• {analysis['rows']:,} rows × {analysis['cols']} columns")
    parts.append(f"• {analysis['missing']:,} missing values ({_pct(analysis['missing'], analysis['rows'] * analysis['cols'])} of all cells)")
    parts.append(f"• {analysis['dupes']:,} duplicate rows ({_pct(analysis['dupes'], analysis['rows'])} of rows)")
    parts.append("")
    
    # ─── 2. Data Quality Insights ───────────────────────────────────────
    quality_issues = []
    if analysis['missing'] > 0:
        quality_issues.append(f"⚠️ **Missing data**: {analysis['missing']:,} missing values detected")
    if analysis['dupes'] > 0:
        quality_issues.append(f"⚠️ **Duplicates**: {analysis['dupes']:,} duplicate rows found")
    if analysis['missing'] == 0 and analysis['dupes'] == 0:
        quality_issues.append("✅ **Clean dataset**: No missing values or duplicates detected")
    
    if quality_issues:
        parts.append("🔍 **Data Quality**")
        for issue in quality_issues:
            parts.append(f"• {issue}")
        parts.append("")
    
    # ─── 3. Numeric Column Insights ─────────────────────────────────────
    if analysis.get('num_stats'):
        parts.append("🔢 **Numeric Column Analysis**")
        for s in analysis['num_stats']:
            spread = float(s['max']) - float(s['min'])
            range_desc = _describe_range(spread, float(s['mean']))
            parts.append(
                f"• **{s['col']}**: Mean={s['mean']}, Median={s['median']}, "
                f"Range=({s['min']}–{s['max']}), {range_desc}"
            )
        parts.append("")
    
    # ─── 4. Correlation Insights ────────────────────────────────────────
    if analysis.get('corr') is not None and data is not None:
        corr_matrix = analysis['corr']
        # Find strongest correlations (excluding self-correlations)
        pairs = []
        for i in corr_matrix.columns:
            for j in corr_matrix.columns:
                if i < j:
                    val = corr_matrix.loc[i, j]
                    pairs.append((i, j, val))
        pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        
        strong_pairs = [p for p in pairs if abs(p[2]) >= 0.3]
        if strong_pairs:
            parts.append("📈 **Correlation Insights**")
            for i, j, val in strong_pairs[:5]:
                direction = "positive" if val > 0 else "negative"
                strength = "strong" if abs(val) >= 0.7 else "moderate"
                emoji = "📈" if val > 0 else "📉"
                parts.append(
                    f"{emoji} **{i}** & **{j}**: {strength} {direction} correlation ({val:.2f})"
                )
            if not strong_pairs:
                parts.append("• No strong correlations found between numeric columns")
            parts.append("")
    
    # ─── 5. Outlier Detection ───────────────────────────────────────────
    if data is not None and analysis.get('num_stats'):
        outlier_cols = []
        for s in analysis['num_stats']:
            col = s['col']
            v = data[col].dropna()
            if len(v) > 0:
                Q1 = v.quantile(0.25)
                Q3 = v.quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outliers = v[(v < lower) | (v > upper)]
                if len(outliers) > 0:
                    pct = (len(outliers) / len(v)) * 100
                    if pct > 1:  # Only flag if >1% are outliers
                        outlier_cols.append((col, len(outliers), pct))
        
        if outlier_cols:
            parts.append("⚠️ **Outlier Detection**")
            for col, count, pct in outlier_cols[:3]:
                parts.append(f"• **{col}**: {count:,} outliers detected ({pct:.1f}% of values)")
            parts.append("")
    
    # ─── 6. Categorical Insights ────────────────────────────────────────
    if analysis.get('cat_stats'):
        parts.append("🏷️ **Categorical Patterns**")
        for s in analysis['cat_stats']:
            top_items = list(s['top'].items())
            if top_items:
                top_name, top_count = top_items[0]
                total = s['count']
                top_pct = (top_count / total * 100) if total > 0 else 0
                parts.append(
                    f"• **{s['col']}**: {s['unique']:,} unique values. "
                    f"Most common: **{top_name}** ({top_count:,}, {top_pct:.1f}%)"
                )
                if len(top_items) > 1:
                    second_count = top_items[1][1]
                    ratio = top_count / second_count if second_count > 0 else 0
                    if ratio > 2:
                        parts.append(f"  └ Dominant category is {ratio:.0f}× more frequent than the next")
        parts.append("")
    
    # ─── 7. Actionable Suggestions ──────────────────────────────────────
    parts.append("💡 **Suggestions**")
    suggestions = []
    
    # Suggest based on correlations
    if analysis.get('corr') is not None:
        corr_matrix = analysis['corr']
        pairs = []
        for i in corr_matrix.columns:
            for j in corr_matrix.columns:
                if i < j:
                    val = corr_matrix.loc[i, j]
                    pairs.append((i, j, abs(val)))
        pairs.sort(key=lambda x: x[2], reverse=True)
        if pairs and pairs[0][2] >= 0.5:
            i, j, val = pairs[0]
            suggestions.append(
                f"Explore the relationship between **{i}** and **{j}** — "
                f"they show a strong correlation ({val:.2f})"
            )
    
    # Suggest based on missing values
    if analysis['missing'] > 0 and data is not None:
        missing_cols = data.isnull().sum()
        missing_cols = missing_cols[missing_cols > 0].sort_values(ascending=False)
        if not missing_cols.empty:
            worst = missing_cols.index[0]
            suggestions.append(
                f"Consider imputing or removing **{worst}** column "
                f"({missing_cols[0]:,} missing values)"
            )
    
    # Suggest based on unique values
    if analysis.get('cat_stats'):
        for s in analysis['cat_stats']:
            if s['unique'] > 20:
                suggestions.append(
                    f"Column **{s['col']}** has {s['unique']:,} unique values — "
                    f"consider grouping or binning for better analysis"
                )
                break
    
    # Suggest based on duplicates
    if analysis['dupes'] > 0:
        suggestions.append(
            f"Remove {analysis['dupes']:,} duplicate rows to avoid skewed results"
        )
    
    # Default suggestion
    if not suggestions:
        if data is not None:
            nums = analysis.get('nums', [])
            cats = analysis.get('cats', [])
            if nums and cats:
                suggestions.append(
                    f"Create visualizations to explore **{nums[0]}** across different **{cats[0]}** categories"
                )
            elif nums:
                suggestions.append(
                    f"Generate a scatter plot or histogram for deeper visual analysis"
                )
    
    for s in suggestions:
        parts.append(f"• {s}")
    
    return '\n'.join(parts)


def _pct(part, total):
    """Calculate percentage, handling zero total."""
    if total == 0:
        return "0%"
    return f"{(part / total) * 100:.1f}%"


def _describe_range(spread, mean):
    """Describe whether values are tightly clustered or wide-spread."""
    if mean == 0:
        return "values vary widely" if spread > 0 else "constant values"
    ratio = spread / abs(mean)
    if ratio < 0.5:
        return "tightly clustered values"
    elif ratio < 1.5:
        return "moderate spread"
    elif ratio < 5:
        return "wide spread"
    else:
        return "very wide spread (high variance)"
