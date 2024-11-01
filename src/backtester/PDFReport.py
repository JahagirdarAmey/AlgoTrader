import os
from datetime import datetime

import matplotlib.pyplot as plt
from fpdf import FPDF


class PDFReport(FPDF):
    """Generates PDF report with backtest results"""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font('Arial', 'B', 16)

    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Backtest Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def metrics_table(self, metrics):
        self.set_font('Arial', 'B', 12)
        col_width = self.w / 2
        line_height = 10

        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                value_str = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
            else:
                value_str = str(value)

            self.cell(col_width, line_height, key, 1)
            self.cell(col_width, line_height, value_str, 1)
            self.ln()

    def add_figure(self, figure, w=190):
        """Add matplotlib figure to PDF"""
        # Save figure to temporary file
        temp_path = f'temp_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.png'
        figure.savefig(temp_path, bbox_inches='tight', dpi=300)
        # Add to PDF
        self.image(temp_path, x=10, w=w)
        self.ln(5)
        # Clean up
        plt.close(figure)
        os.remove(temp_path)