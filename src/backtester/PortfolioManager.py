class PortfolioManager:
    """Manages portfolio positions and capital"""

    def __init__(self, initial_capital, position_size_percent=2):
        self.capital = initial_capital
        self.position_size_percent = position_size_percent
        self.position = 0
        self.remaining_position = 0
        self.entry_price = 0
        self.entry_date = None

    def calculate_position_size(self, price, atr):
        risk_amount = self.capital * (self.position_size_percent / 100)
        max_position_size = risk_amount / atr if atr > 0 else 0
        return min(max_position_size, self.capital // price)

    def enter_position(self, price, date, units):
        self.entry_price = price
        self.entry_date = date
        self.capital -= units * price
        self.position = units
        self.remaining_position = units
        return {
            'type': 'buy',
            'price': price,
            'date': date,
            'position': units
        }

    def exit_partial_position(self, price, date, percentage):
        sell_units = self.remaining_position * percentage
        self.capital += sell_units * price
        self.remaining_position -= sell_units
        return {
            'type': 'partial sell',
            'price': price,
            'date': date,
            'position': sell_units
        }

    def exit_full_position(self, price, date):
        self.capital += self.remaining_position * price
        units_sold = self.remaining_position
        self.position = 0
        self.remaining_position = 0
        return {
            'type': 'sell',
            'price': price,
            'date': date,
            'position': units_sold
        }

    def get_portfolio_value(self, current_price):
        return self.capital + (self.remaining_position * current_price if self.remaining_position > 0 else 0)
