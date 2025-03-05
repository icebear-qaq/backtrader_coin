import numpy as np

class MomentumStrategy:
    def __init__(self, window=10, threshold=0.02):
        self.window = window
        self.threshold = threshold
        self.closes = np.empty(0)

    def process_kline(self, kline):
        current_close = kline.get_close()
        self.closes = np.append(self.closes, current_close)

        if len(self.closes) < self.window + 1:
            return None

        momentum = (self.closes[-1] - self.closes[-self.window - 1]) / self.closes[-self.window - 1]
        if momentum > self.threshold:
            return 'buy'
        elif momentum < -self.threshold:
            return 'sell'
        return None