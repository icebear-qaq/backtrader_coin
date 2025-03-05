import numpy as np

class KDJStrategy:
    def __init__(self, k_window=9, d_window=3, j_window=3):
        self.k_window = k_window
        self.d_window = d_window
        self.j_window = j_window
        self.closes = np.empty(0)
        self.highs = np.empty(0)
        self.lows = np.empty(0)
        self.k_values = np.empty(0)
        self.d_values = np.empty(0)
        self.j_values = np.empty(0)

    def process_kline(self, kline):
        current_close = kline.get_close()
        current_high = kline.get_high()
        current_low = kline.get_low()
        self.closes = np.append(self.closes, current_close)
        self.highs = np.append(self.highs, current_high)
        self.lows = np.append(self.lows, current_low)

        if len(self.closes) < self.k_window:
            return None

        highest_high = np.max(self.highs[-self.k_window:])
        lowest_low = np.min(self.lows[-self.k_window:])
        if highest_high == lowest_low:
            return None

        k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        self.k_values = np.append(self.k_values, k)

        if len(self.k_values) < self.d_window:
            return None

        d = np.mean(self.k_values[-self.d_window:])
        self.d_values = np.append(self.d_values, d)

        if len(self.d_values) < self.j_window:
            return None

        j = 3 * self.k_values[-1] - 2 * self.d_values[-1]
        self.j_values = np.append(self.j_values, j)

        if len(self.k_values) < 2 or len(self.d_values) < 2:
            return None

        if self.k_values[-2] <= self.d_values[-2] and self.k_values[-1] > self.d_values[-1] and j > 0:
            return 'buy'
        elif self.k_values[-2] >= self.d_values[-2] and self.k_values[-1] < self.d_values[-1] and j < 0:
            return 'sell'
        return None