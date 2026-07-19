"""Generate professional PDF reports — stats, tables, and chart images in one document."""
import os
import numpy as np
from datetime import datetime
from fpdf import FPDF
from config import Settings


class Report(FPDF):
    """Custom PDF with branded header/footer."""

    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(102, 126, 234)
        self.cell(0, 8, 'Data Analysis Report', align='L')
        self.cell(0, 8, datetime.now().strftime('%Y-%m-%d %H:%M'), align='R', new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(102, 126, 234)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(40, 40, 60)
        self.cell(0, 10, title, new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(102, 126, 234)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def sub_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(60, 60, 80)
        self.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT')
        self.ln(2)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def metric_row(self, metrics):
        """Render a row of metric cards (label: value) side by side."""
        col_w = 190 / max(len(metrics), 1)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(102, 126, 234)
        for label, value in metrics:
            self.cell(col_w, 10, str(value), align='C')
        self.ln(6)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(100, 100, 100)
        for label, value in metrics:
            self.cell(col_w, 6, label, align='C')
        self.ln(8)


def generate_pdf_report(data, analysis, dashboard_charts=None, dataset_name="dataset", custom_notes=None):
    """Generate a complete PDF report and return the file path.

    Parameters
    ----------
    data : pd.DataFrame
        The loaded dataset.
    analysis : dict
        Analysis result from run_full_analysis().
    dashboard_charts : list of (title, path) tuples, optional
        Chart images from generate_dashboard().
    dataset_name : str
        Display name for the dataset.
    custom_notes : str, optional
        User-provided notes/annotations to include in the report.

    Returns
    -------
    str or None
        Path to the generated PDF file, or None on failure.
    """
    try:
        os.makedirs(Settings.CHART_DIR, exist_ok=True)
        pdf_path = os.path.join(Settings.CHART_DIR, 'report.pdf')

        pdf = Report()
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=20)

        # ── Page 1: Title & Overview ───────────────────────────────────────
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 24)
        pdf.set_text_color(40, 40, 60)
        pdf.ln(20)
        pdf.cell(0, 15, 'Data Analysis Report', align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('Helvetica', '', 12)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, f'Dataset: {dataset_name}', align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.cell(0, 8, f'Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")}', align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(10)
        pdf.set_draw_color(102, 126, 234)
        pdf.line(60, pdf.get_y(), 150, pdf.get_y())
        pdf.ln(10)

        # Overview metrics
        pdf.section_title('Dataset Overview')
        pdf.metric_row([
            ('Rows', f'{analysis["rows"]:,}'),
            ('Columns', f'{analysis["cols"]}'),
            ('Missing', f'{analysis["missing"]:,}'),
            ('Duplicates', f'{analysis["dupes"]:,}'),
        ])

        # Column type breakdown
        nums = analysis['nums']
        cats = analysis['cats']
        dates = analysis['dates']
        pdf.body_text(
            f'Column Types:  {len(nums)} numeric  |  {len(cats)} categorical  |  {len(dates)} date'
        )
        pdf.ln(4)

        # Data quality
        pdf.section_title('Data Quality')
        quality_notes = []
        if analysis['missing'] > 0:
            quality_notes.append(f'- Missing values: {analysis["missing"]:,}')
        if analysis['dupes'] > 0:
            quality_notes.append(f'- Duplicate rows: {analysis["dupes"]:,}')
        if not quality_notes:
            quality_notes.append('- No missing values or duplicates detected. Dataset is clean!')
        pdf.body_text('\n'.join(quality_notes))

        # ── Numeric columns ────────────────────────────────────────────────
        if analysis.get('num_stats'):
            pdf.add_page()
            pdf.section_title('Numeric Column Statistics')

            # Table header
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_fill_color(102, 126, 234)
            pdf.set_text_color(255, 255, 255)
            col_widths = [50, 25, 25, 25, 25, 25]
            headers = ['Column', 'Count', 'Mean', 'Median', 'Min', 'Max']
            for h, w in zip(headers, col_widths):
                pdf.cell(w, 8, h, border=1, fill=True, align='C')
            pdf.ln()

            # Table rows
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(50, 50, 50)
            for i, s in enumerate(analysis['num_stats']):
                if i % 2 == 0:
                    pdf.set_fill_color(245, 247, 255)
                else:
                    pdf.set_fill_color(255, 255, 255)
                pdf.cell(col_widths[0], 7, str(s['col'])[:25], border=1, fill=True)
                pdf.cell(col_widths[1], 7, f"{s['count']:,}", border=1, fill=True, align='C')
                pdf.cell(col_widths[2], 7, f"{s['mean']:.2f}", border=1, fill=True, align='C')
                pdf.cell(col_widths[3], 7, f"{s['median']:.2f}", border=1, fill=True, align='C')
                pdf.cell(col_widths[4], 7, f"{s['min']:.2f}", border=1, fill=True, align='C')
                pdf.cell(col_widths[5], 7, f"{s['max']:.2f}", border=1, fill=True, align='C')
                pdf.ln()

        # ── Categorical columns ────────────────────────────────────────────
        if analysis.get('cat_stats'):
            pdf.add_page()
            pdf.section_title('Categorical Column Statistics')

            for s in analysis['cat_stats']:
                pdf.sub_title(f'{s["col"]}  ({s["unique"]:,} unique values)')
                top_items = list(s['top'].items())[:5]
                if top_items:
                    pdf.set_font('Helvetica', '', 9)
                    pdf.set_text_color(50, 50, 50)
                    for k, v in top_items:
                        pct = (v / s['count'] * 100) if s['count'] > 0 else 0
                        pdf.cell(5)
                        pdf.cell(0, 6, f'- {k}: {v:,} ({pct:.1f}%)', new_x='LMARGIN', new_y='NEXT')
                pdf.ln(3)

        # ── Correlation highlights ─────────────────────────────────────────
        if analysis.get('corr') is not None:
            corr = analysis['corr']
            pairs = []
            for i in corr.columns:
                for j in corr.columns:
                    if i < j:
                        val = corr.loc[i, j]
                        pairs.append((i, j, abs(val), val))
            pairs.sort(key=lambda x: x[2], reverse=True)

            strong = [p for p in pairs if p[2] >= 0.3]
            if strong:
                pdf.add_page()
                pdf.section_title('Key Correlations')
                for i, j, _, val in strong[:6]:
                    direction = 'positive' if val > 0 else 'negative'
                    strength = 'strong' if abs(val) >= 0.7 else 'moderate'
                    pdf.body_text(f'- {i} & {j}: {strength} {direction} ({val:.3f})')

        # ── Dashboard Charts ───────────────────────────────────────────────
        if dashboard_charts:
            pdf.add_page()
            pdf.section_title('Visualizations')

            for title, chart_path in dashboard_charts:
                if os.path.exists(chart_path):
                    # Check if we need a new page (2 charts per page)
                    if pdf.get_y() > 160:
                        pdf.add_page()

                    pdf.sub_title(title)
                    # Image dimensions to fit page width
                    page_w = pdf.w - 20  # 190mm
                    img_h = 80
                    try:
                        pdf.image(chart_path, x=10, w=page_w, h=img_h)
                        pdf.ln(4)
                    except Exception:
                        pdf.body_text('(Chart image could not be embedded)')
                    pdf.ln(4)

        # ── Custom Notes ──────────────────────────────────────────────────
        if custom_notes and custom_notes.strip():
            pdf.add_page()
            pdf.section_title('Custom Notes')
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(50, 50, 50)

            # Render each line, preserving paragraph breaks
            paragraphs = custom_notes.strip().split('\n\n')
            for para in paragraphs:
                lines = para.strip().split('\n')
                for line in lines:
                    # Check if it looks like a bullet point
                    if line.strip().startswith('-') or line.strip().startswith('•'):
                        pdf.cell(5)
                        pdf.multi_cell(0, 6, line.strip())
                    else:
                        pdf.multi_cell(0, 6, line.strip())
                pdf.ln(3)

            # Footer with date
            pdf.ln(5)
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(130, 130, 130)
            pdf.cell(0, 6, f'Notes added: {datetime.now().strftime("%B %d, %Y")}',
                     new_x='LMARGIN', new_y='NEXT')

        # ── Save ───────────────────────────────────────────────────────────
        pdf.output(pdf_path)
        return pdf_path

    except Exception as e:
        print(f'PDF report error: {e}')
        return None
