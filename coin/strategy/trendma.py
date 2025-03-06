import numpy as np

class MATrendFollowingStrategy:
    def __init__(self, window=50):
        self.window = window
        self.closes = np.empty(0)
        self.ma = None

    def process_kline(self, kline):
        current_close = kline.get_close()
        self.closes = np.append(self.closes, current_close)

        if len(self.closes) < self.window + 1:
            return None

        ma = np.mean(self.closes[-self.window:])
        if self.ma is None:
            self.ma = ma
            return None

        ma_direction = ma - self.ma
        self.ma = ma

        if current_close > ma and ma_direction > 0:
            return 'buy'
        elif current_close < ma and ma_direction < 0:
            return 'sell'
        return None