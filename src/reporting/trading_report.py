import os
import logging
from datetime import datetime
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import pandas as pd
import matplotlib.dates as mdates


class TradingReport:
    def __init__(self, config, results, analysis):
        self.config = config
        self.results = results
        self.analysis = analysis
        # Calculate final portfolio value from the equity curve if available
        self.final_portfolio_value = (
            self.results.get('equity_curve', [])[-1]
            if self.results.get('equity_curve') and len(self.results.get('equity_curve', [])) > 0
            else self.config.initial_capital + self.analysis.get('total_profit', 0)
        )
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = "../logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, "logs.txt")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_charts(self):
        """Create trading charts with buy/sell signals"""
        plt.figure(figsize=(12, 6))

        # Check if we have the required data
        if not all(key in self.results for key in ['dates', 'prices']):
            self.logger.warning("Missing required price data for charts")
            # Create a simple placeholder chart
            plt.text(0.5, 0.5, 'Insufficient data for chart',
                     horizontalalignment='center', verticalalignment='center')
            chart_path = 'trading_chart.png'
            plt.savefig(chart_path)
            plt.close()
            return chart_path

        plt.plot(self.results['dates'], self.results['prices'], label='Price')

        # Plot EMAs if available
        if 'ema_short' in self.results:
            plt.plot(self.results['dates'], self.results['ema_short'],
                     label=f'EMA {self.config.ema_short}')
        if 'ema_long' in self.results:
            plt.plot(self.results['dates'], self.results['ema_long'],
                     label=f'EMA {self.config.ema_long}')

        # Plot signals if available
        if 'buy_dates' in self.results and 'buy_prices' in self.results:
            plt.scatter(self.results['buy_dates'], self.results['buy_prices'],
                        color='green', marker='^', label='Buy Signal')
        if 'sell_dates' in self.results and 'sell_prices' in self.results:
            plt.scatter(self.results['sell_dates'], self.results['sell_prices'],
                        color='red', marker='v', label='Sell Signal')

        plt.title(f'Trading Chart for {self.config.symbol}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)

        chart_path = 'trading_chart.png'
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    def create_equity_curve(self):
        """Create equity curve chart"""
        plt.figure(figsize=(12, 6))

        dates = self.results.get('dates', [])
        equity_curve = self.results.get('equity_curve', [])

        if not dates or not equity_curve:
            self.logger.warning("Missing equity curve data")
            # Create a simple placeholder chart
            plt.text(0.5, 0.5, 'Insufficient data for equity curve',
                     horizontalalignment='center', verticalalignment='center')
        else:
            # Ensure both lists have the same length
            min_length = min(len(dates), len(equity_curve))
            dates = dates[:min_length]
            equity_curve = equity_curve[:min_length]

            plt.plot(dates, equity_curve, label='Equity Curve')

        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')
        plt.grid(True)

        equity_path = 'equity_curve.png'
        plt.savefig(equity_path)
        plt.close()
        return equity_path

    def generate_pdf_report(self):
        """Generate PDF report with all trading statistics and charts"""
        report_filename = f"trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(report_filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph(f"Trading Report - {self.config.symbol}", title_style))
        story.append(Spacer(1, 20))

        # Configuration Section
        story.append(Paragraph("Trading Configuration", styles['Heading2']))
        config_data = [
            ["Parameter", "Value"],
            ["Symbol", self.config.symbol],
            ["Start Date", self.config.start_date],
            ["End Date", self.config.end_date],
            ["Initial Capital", f"${self.config.initial_capital:,.2f}"],
            ["EMA Short", str(self.config.ema_short)],
            ["EMA Long", str(self.config.ema_long)],
            ["Volume Threshold", str(self.config.volume_threshold)],
            ["Stop Loss", f"{self.config.stop_loss:.1%}"],
            ["Take Profit", f"{self.config.take_profit:.1%}"]
        ]

        config_table = Table(config_data)
        config_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(config_table)
        story.append(Spacer(1, 20))

        # Performance Metrics
        story.append(Paragraph("Performance Metrics", styles['Heading2']))
        metrics_data = [
            ["Metric", "Value"],
            ["Total Trades", str(self.analysis.get('total_trades', 0))],
            ["Winning Trades", str(self.analysis.get('winning_trades', 0))],
            ["Win Rate",
             f"{self.analysis.get('winning_trades', 0) / max(self.analysis.get('total_trades', 1), 1):.1%}"],
            ["Total Profit", f"${self.analysis.get('total_profit', 0):,.2f}"],
            ["Max Drawdown", f"{self.analysis.get('max_drawdown', 0):.1%}"],
            ["Sharpe Ratio", f"{self.analysis.get('sharpe_ratio', 0):.2f}"],
            ["Final Portfolio Value", f"${self.final_portfolio_value:,.2f}"]
        ]

        metrics_table = Table(metrics_data)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 20))

        # Add charts
        story.append(Paragraph("Trading Charts", styles['Heading2']))
        chart_path = self.create_charts()
        story.append(Image(chart_path, width=500, height=300))
        story.append(Spacer(1, 20))

        story.append(Paragraph("Equity Curve", styles['Heading2']))
        equity_path = self.create_equity_curve()
        story.append(Image(equity_path, width=500, height=300))

        # Generate PDF
        doc.build(story)
        self.logger.info(f"PDF report generated: {report_filename}")

        # Clean up temporary image files
        os.remove(chart_path)
        os.remove(equity_path)

        return report_filename

    def generate_report(self):
        """Main method to generate the complete report"""
        self.logger.info("Starting report generation...")
        self.logger.info(f"Initial investment: ${self.config.initial_capital:,.2f}")
        self.logger.info(f"Final portfolio value: ${self.final_portfolio_value:,.2f}")
        self.logger.info(
            f"Total return: {((self.final_portfolio_value - self.config.initial_capital) / self.config.initial_capital):,.2%}")

        report_file = self.generate_pdf_report()
        self.logger.info("Report generation completed.")
        return report_file