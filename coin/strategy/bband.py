import numpy as np
import pandas as pd
from numba import jit


class BollingerRSIStrategy:
    def __init__(self, bollinger_window=20, bollinger_std=2, rsi_window=14, rsi_threshold=70):
        self.bollinger_window = bollinger_window
        self.bollinger_std = bollinger_std
        self.rsi_window = rsi_window
        self.rsi_threshold = rsi_threshold
        self.prices = []  # 用于存储历史价格

    def calculate_bollinger_bands(self):
        """
        计算布林带
        """
        if len(self.prices) < self.bollinger_window:
            return None, None, None

        prices = np.array(self.prices[-self.bollinger_window:])
        ma = np.mean(prices)
        std = np.std(prices)
        upper_band = ma + self.bollinger_std * std
        lower_band = ma - self.bollinger_std * std
        return ma, upper_band, lower_band
    def calculate_rsi(self):
        """
        计算RSI
        """
        if len(self.prices) < self.rsi_window:
            return None

        prices = np.array(self.prices[-self.rsi_window:])
        delta = np.diff(prices)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = np.mean(gain)
        avg_loss = np.mean(loss)
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def process_kline(self, kline):
        """
        处理单根K线，生成交易信号
        :param kline: Kline 对象
        :return: 交易信号 ('sell' 或 None)
        """
        current_price = kline.get_close()
        self.prices.append(current_price)

        # 计算布林带
        _, upper_band, _ = self.calculate_bollinger_bands()
        if upper_band is None:
            return None

        # 计算RSI
        rsi = self.calculate_rsi()
        if rsi is None:
            return None

        # 生成交易信号
        if current_price < upper_band and rsi > self.rsi_threshold:
            return 'sell'
        return None