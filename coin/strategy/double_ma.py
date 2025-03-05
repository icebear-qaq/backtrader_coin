import numpy as np
from numba import jit


# 计算简单移动平均线 (SMA)
def calculate_sma(prices, window):
    """
    计算简单移动平均线 (Simple Moving Average)
    :param prices: 价格数组
    :param window: 计算窗口大小
    :return: 简单移动平均值
    """
    if len(prices) < window:
        return None
    return np.mean(prices[-window:])


# 计算指数移动平均线 (EMA)
def calculate_ema(prices, window):
    """
    计算指数移动平均线 (Exponential Moving Average)
    :param prices: 价格数组
    :param window: 计算窗口大小
    :return: 指数移动平均值
    """
    if len(prices) < window:
        return None

    # 使用 pandas 的 ewm 方法计算 EMA
    multiplier = 2 / (window + 1)
    prices = np.array(prices)
    initial_sma = np.mean(prices[-window:])  # 初始值为 SMA
    ema = initial_sma
    for price in prices[-window + 1:]:
        ema = (price - ema) * multiplier + ema
    return ema


class DoubleMAStrategy:
    def __init__(self, short_window=10, long_window=30, ma_type='sma'):
        """
        初始化双均线交易策略
        :param short_window: 短期均线的窗口大小
        :param long_window: 长期均线的窗口大小
        :param ma_type: 均线类型 ('sma' 或 'ema')
        """
        self.short_window = short_window
        self.long_window = long_window
        self.ma_type = ma_type.lower()
        if self.ma_type not in ['sma', 'ema']:
            raise ValueError("ma_type must be 'sma' or 'ema'")

        self.closes = np.empty(0)  # 使用 NumPy 数组存储收盘价
        self.short_ma = None  # 上一次计算的短期均线
        self.long_ma = None  # 上一次计算的长期均线

    def process_kline(self, kline):
        """
        处理单根 K 线，生成交易信号
        :param kline: Kline 对象，包含 close 属性
        :return: 交易信号 ('sell' 或 'buy' 或 None)
        """
        current_close = kline.get_close()

        # 更新价格数据
        self.closes = np.append(self.closes, current_close)

        # 根据 ma_type 选择计算 SMA 或 EMA
        if self.ma_type == 'sma':
            short_ma = calculate_sma(self.closes, self.short_window)
            long_ma = calculate_sma(self.closes, self.long_window)
        else:  # self.ma_type == 'ema'
            short_ma = calculate_ema(self.closes, self.short_window)
            long_ma = calculate_ema(self.closes, self.long_window)

        # 如果均线值未计算出来（数据不足），返回 None
        if short_ma is None or long_ma is None:
            return None

        # 检查是否满足双均线交叉条件
        if self.short_ma is not None and self.long_ma is not None:
            # 金叉做多：短期均线从下向上穿越长期均线
            if self.short_ma <= self.long_ma and short_ma > long_ma:
                self.short_ma = short_ma
                self.long_ma = long_ma
                return 'buy'
            # 死叉做空：短期均线从上向下穿越长期均线
            elif self.short_ma >= self.long_ma and short_ma < long_ma:
                self.short_ma = short_ma
                self.long_ma = long_ma
                return 'sell'

        # 更新均线值
        self.short_ma = short_ma
        self.long_ma = long_ma
        return None