from datetime import datetime

from src.backtester import BacktestMetrics, ReportVisualizer, PDFReport


class BacktestReporter:
    """Main class for generating backtest reports"""

    def __init__(self, results):
        self.results = results
        self.metrics = BacktestMetrics()  # Using the previously defined BacktestMetrics class
        self.visualizer = ReportVisualizer()

    def generate_report(self):
        # Calculate metrics
        portfolio_values = self.results['portfolio_df']['portfolio_value'].values
        dates = self.results['portfolio_df']['date'].values

        returns_metrics = self.metrics.calculate_returns_metrics(portfolio_values)
        drawdown_metrics = self.metrics.calculate_drawdown_metrics(portfolio_values)
        trade_metrics = self.metrics.calculate_trade_metrics(self.results['trades_df'])

        future_predictions = self.metrics.predict_future_returns(
            portfolio_values[-1],
            returns_metrics['Annualized Return (%)'] / 100
        )

        # Generate PDF
        pdf = PDFReport()

        # Overview
        pdf.chapter_title('Strategy Overview')
        pdf.chapter_body(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Performance Metrics
        pdf.chapter_title('Performance Metrics')
        pdf.metrics_table({
            'Initial Balance': f"${self.results['portfolio_df']['portfolio_value'].iloc[0]:,.2f}",
            'Final Balance': f"${self.results['portfolio_df']['portfolio_value'].iloc[-1]:,.2f}",
            **returns_metrics,
            **drawdown_metrics,
            **trade_metrics
        })

        # Future Predictions
        pdf.chapter_title('Projected Returns')
        pdf.metrics_table({
            'Projected 1 Month': f"${future_predictions['1 Month']:,.2f}",
            'Projected 12 Months': f"${future_predictions['12 Months']:,.2f}",
            'Projected 10 Years': f"${future_predictions['10 Years']:,.2f}"
        })

        # Trading Strategy Analysis
        pdf.add_page()
        pdf.chapter_title('Trading Strategy Analysis')

        # Calculate duration info for trading strategy plot
        start_date = self.results['signals_data'].index[0]
        end_date = self.results['signals_data'].index[-1]
        duration_days = (end_date - start_date).days
        duration_months = duration_days // 30
        duration_remainder = duration_days % 30
        duration_info = f"{duration_days} days (~{duration_months} months and {duration_remainder} days)"

        # Create and add trading strategy plot
        strategy_fig = self.visualizer.create_trading_strategy_plot(
            self.results['signals_data'],
            self.results['trades_df'],
            start_date,
            end_date,
            duration_info
        )
        pdf.add_figure(strategy_fig)

        # Create and add other visualizations
        pdf.add_page()
        pdf.chapter_title('Performance Charts')

        equity_fig = self.visualizer.create_equity_curve(portfolio_values, dates)
        pdf.add_figure(equity_fig)

        drawdown_fig = self.visualizer.create_drawdown_chart(portfolio_values, dates)
        pdf.add_figure(drawdown_fig)

        returns_fig = self.visualizer.create_monthly_returns_heatmap(portfolio_values, dates)
        pdf.add_figure(returns_fig)

        # Save report
        pdf_path = f"backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(pdf_path)

        return pdf_path

