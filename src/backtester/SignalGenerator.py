class SignalGenerator:
    """Generates trading signals based on technical indicators"""

    @staticmethod
    def generate_signals(data):
        data['Signal'] = 0

        buy_conditions = (
                (data['Rsi'] < 30) &
                (data['Close'] > data['Vwap']) &
                (data['Volume'] > data['Volume'].rolling(20).mean() * 1.2)
        )

        sell_conditions = (
                (data['Rsi'] > 70) |
                (data['Close'] < data['Bb_Lower'])
        )

        data.loc[buy_conditions, 'Signal'] = 1
        data.loc[sell_conditions, 'Signal'] = -1
        return data