import numpy as np
from numba import jit

# 计算RSI
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


# 计算基于RSI的布林带
def calculate_rsi_bollinger_bands(rsis, window, num_std=2):
    """
    计算基于RSI值的布林带
    :param rsis: RSI值数组
    :param window: 布林带的计算窗口大小
    :param num_std: 标准差倍数，默认为2
    :return: 布林带上轨、中轨和下轨
    """
    if len(rsis) < window:
        return None, None, None

    sma = np.mean(rsis[-window:])
    std = np.std(rsis[-window:])
    upper_band = sma + num_std * std
    lower_band = sma - num_std * std

    return upper_band, sma, lower_band


class RSIBollingerStrategy:
    def __init__(self, rsi_window=14, boll_window=20, boll_num_std=2):
        """
        初始化基于RSI和布林带的交易策略
        :param rsi_window: RSI的计算窗口大小
        :param boll_window: 布林带的计算窗口大小
        :param boll_num_std: 布林带的标准差倍数
        """
        self.rsi_window = rsi_window
        self.boll_window = boll_window
        self.boll_num_std = boll_num_std
        self.closes = np.empty(0)  # 使用NumPy数组存储收盘价
        self.rsis = np.empty(0)   # 使用NumPy数组存储RSI值
        self.upper_band = None    # 上一次计算的布林带上轨
        self.lower_band = None    # 上一次计算的布林带下轨

    def process_kline(self, kline):
        """
        处理单根K线，生成交易信号
        :param kline: Kline对象，包含close属性
        :return: 交易信号 ('sell' 或 'buy' 或 None)
        """
        current_close = kline.get_close()

        # 更新价格数据
        self.closes = np.append(self.closes, current_close)

        # 计算RSI
        rsi = calculate_rsi(self.closes, self.rsi_window)
        if rsi is None:
            return None

        # 更新RSI数据
        self.rsis = np.append(self.rsis, rsi)

        # 计算基于RSI的布林带
        upper_band, _, lower_band = calculate_rsi_bollinger_bands(self.rsis, self.boll_window, self.boll_num_std)
        if upper_band is None or lower_band is None:
            return None

        # 检查是否满足“回踩”或“回穿”条件
        if self.upper_band is not None and self.lower_band is not None:
            # 回踩上轨做空：RSI穿过上轨后又向下穿越
            if self.rsis[-2] > self.upper_band and rsi < upper_band:
                return 'sell'
            # 回穿下轨做多：RSI穿过下轨后又向上穿越
            elif self.rsis[-2] < self.lower_band and rsi > lower_band:
                return 'buy'

        # 更新布林带上下轨
        self.upper_band = upper_band
        self.lower_band = lower_band
        return None