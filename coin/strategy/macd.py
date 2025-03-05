import numpy as np

class MACDStrategy:
    def __init__(self, fast_window=12, slow_window=26, signal_window=9):
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.signal_window = signal_window
        self.closes = np.empty(0)
        self.macds = np.empty(0)
        self.signals = np.empty(0)

    def calculate_ema(self, prices, window):
        if len(prices) < window:
            return None
        multiplier = 2 / (window + 1)
        ema = np.mean(prices[-window:])
        for price in prices[-window + 1:]:
            ema = (price - ema) * multiplier + ema
        return ema

    def process_kline(self, kline):
        current_close = kline.get_close()
        self.closes = np.append(self.closes, current_close)

        fast_ema = self.calculate_ema(self.closes, self.fast_window)
        slow_ema = self.calculate_ema(self.closes, self.slow_window)
        if fast_ema is None or slow_ema is None:
            return None

        macd = fast_ema - slow_ema
        self.macds = np.append(self.macds, macd)

        if len(self.macds) < self.signal_window:
            return None

        signal = self.calculate_ema(self.macds, self.signal_window)
        self.signals = np.append(self.signals, signal)

        if len(self.signals) < 2 or len(self.macds) < 2:
            return None

        if self.macds[-2] <= self.signals[-2] and self.macds[-1] > self.signals[-1]:
            return 'buy'
        elif self.macds[-2] >= self.signals[-2] and self.macds[-1] < self.signals[-1]:
            return 'sell'
        return None