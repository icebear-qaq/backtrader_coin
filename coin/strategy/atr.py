import numpy as np
from numba import jit

# 提取为独立函数
@jit(nopython=True)
def calculate_atr(highs, lows, closes, window):
    """
    计算ATR（Average True Range）
    """
    n = len(closes)
    if n < window:
        return None

    tr_values = np.zeros(n)
    for i in range(n):
        if i == 0:
            tr_values[i] = highs[i] - lows[i]
        else:
            high_low_range = highs[i] - lows[i]
            high_prev_close = abs(highs[i] - closes[i - 1])
            low_prev_close = abs(lows[i] - closes[i - 1])
            tr_values[i] = max(high_low_range, high_prev_close, low_prev_close)

    atr = np.mean(tr_values[-window:])
    return atr


@jit(nopython=True)
def calculate_sma(prices, window):
    """
    计算简单移动平均线（SMA）
    """
    if len(prices) < window:
        return None
    sma = np.mean(prices[-window:])
    return sma


@jit(nopython=True)
def calculate_rsi(prices, window):
    """
    计算RSI（Relative Strength Index）
    """
    if len(prices) < window + 1:  # RSI需要至少 window + 1 个数据点
        return None

    changes = np.diff(prices)  # 计算价格变化
    gains = np.where(changes > 0, changes, 0)  # 上涨部分
    losses = np.where(changes < 0, np.abs(changes), 0)  # 下跌部分

    avg_gain = np.mean(gains[-window:])
    avg_loss = np.mean(losses[-window:])

    if avg_loss == 0:
        return 100  # 避免除以零

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


class ATRSellStrategy:
    def __init__(self, atr_window=14, atr_threshold=1.5, sma_window=20, rsi_window=14, rsi_threshold=65):
        """
        初始化ATR卖出策略
        :param atr_window: ATR的计算窗口大小
        :param atr_threshold: 用于判断卖出信号的ATR阈值
        :param sma_window: 简单移动平均线的窗口大小
        :param rsi_window: RSI的计算窗口大小
        :param rsi_threshold: 用于判断超买的RSI阈值
        """
        self.atr_window = atr_window
        self.atr_threshold = atr_threshold
        self.sma_window = sma_window
        self.rsi_window = rsi_window
        self.rsi_threshold = rsi_threshold
        self.highs = np.empty(0)   # 使用NumPy数组存储最高价
        self.lows = np.empty(0)    # 使用NumPy数组存储最低价
        self.closes = np.empty(0)  # 使用NumPy数组存储收盘价

    def process_kline(self, kline):
        """
        处理单根K线，生成卖出信号
        :param kline: Kline对象，包含high、low、close三个属性
        :return: 交易信号 ('sell' 或 None)
        """
        current_high = kline.get_high()
        current_low = kline.get_low()
        current_close = kline.get_close()

        # 更新价格数据
        self.highs = np.append(self.highs, current_high)
        self.lows = np.append(self.lows, current_low)
        self.closes = np.append(self.closes, current_close)

        # 计算ATR
        atr = calculate_atr(self.highs, self.lows, self.closes, self.atr_window)
        if atr is None:
            return None

        # 计算SMA
        sma = calculate_sma(self.closes, self.sma_window)
        if sma is None:
            return None

        # 计算RSI
        rsi = calculate_rsi(self.closes, self.rsi_window)
        if rsi is None:
            return None

        # 生成卖出信号
        if atr > self.atr_threshold and current_close > sma and rsi > self.rsi_threshold:
            return 'sell'
        return None