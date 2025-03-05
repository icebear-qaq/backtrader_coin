import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt

from coin.back_result import back_result


class FakeBroker:
    def __init__(self, initial_balance=10000, leverage=10, fee_rate=0.0004, open_ratio=0.2, stop_loss=0.5,
                 take_profit=2.0):
        self.initial_balance = initial_balance
        self.leverage = leverage
        self.fee_rate = fee_rate
        self.open_ratio = open_ratio
        self.stop_loss = stop_loss
        self.take_profit = take_profit

        self.balance = initial_balance
        self.long_position = 0
        self.short_position = 0
        self.long_position_price = 0
        self.short_position_price = 0
        self.long_margin = 0
        self.short_margin = 0

        self.history = []

    def buy(self, price, timestamp, open_ratio=None):
        open_ratio = open_ratio if open_ratio is not None else self.open_ratio
        if self.long_position == 0:
            margin = self.balance * open_ratio
            quantity = (margin * self.leverage) / price
            if margin <= self.balance:
                self.balance -= margin
                self.long_position = quantity
                self.long_position_price = price
                self.long_margin = margin

                # 计算止损和止盈价格（考虑杠杆）
                stop_loss_price = price * (1 - self.stop_loss / self.leverage)
                take_profit_price = price * (1 + self.take_profit / self.leverage)

                # 手续费
                fee = margin * self.leverage * self.fee_rate

                self.history.append({
                    'type': 'buy',
                    'price': price,
                    'quantity': quantity,
                    'balance': self.balance,
                    'position': self.long_position,
                    'margin': margin,
                    'stop_loss_price': stop_loss_price,
                    'take_profit_price': take_profit_price,
                    'fee': fee,
                    'timestamp': timestamp  # 记录开仓时间
                })
                self.balance -= fee
            else:
                raise ValueError("余额不足，无法开多仓")

    def sell(self, price, timestamp, open_ratio=None):
        open_ratio = open_ratio if open_ratio is not None else self.open_ratio
        if self.short_position == 0:
            margin = self.balance * open_ratio
            quantity = (margin * self.leverage) / price
            if margin <= self.balance:
                self.balance -= margin
                self.short_position = quantity
                self.short_position_price = price
                self.short_margin = margin

                # 计算止损和止盈价格（考虑杠杆）
                stop_loss_price = price * (1 + self.stop_loss / self.leverage)
                take_profit_price = price * (1 - self.take_profit / self.leverage)

                fee = margin * self.leverage * self.fee_rate

                self.history.append({
                    'type': 'sell',
                    'price': price,
                    'quantity': quantity,
                    'balance': self.balance,
                    'position': -self.short_position,
                    'margin': margin,
                    'stop_loss_price': stop_loss_price,
                    'take_profit_price': take_profit_price,
                    'fee': fee,
                    'timestamp': timestamp  # 记录开仓时间
                })
                self.balance -= fee
            else:
                raise ValueError("余额不足，无法开空仓")

    def close_long(self, price, timestamp, reason='normal'):
        if self.long_position > 0:
            profit = (self.long_position * price) - (self.long_position * self.long_position_price)
            self.balance += self.long_margin + profit
            fee = self.long_margin * self.leverage * self.fee_rate
            self.history.append({
                'type': 'close_long',
                'price': price,
                'quantity': self.long_position,
                'balance': self.balance,
                'position': 0,
                'profit': profit,
                'fee': fee,
                'reason': reason,
                'timestamp': timestamp  # 记录平仓时间
            })
            self.balance -= fee
            self.long_position = 0
            self.long_position_price = 0
            self.long_margin = 0

    def close_short(self, price, timestamp, reason='normal'):
        if self.short_position > 0:
            profit = (self.short_position * self.short_position_price) - (self.short_position * price)
            self.balance += self.short_margin + profit
            fee = self.short_margin * self.leverage * self.fee_rate
            self.history.append({
                'type': 'close_short',
                'price': price,
                'quantity': self.short_position,
                'balance': self.balance,
                'position': 0,
                'profit': profit,
                'fee': fee,
                'reason': reason,
                'timestamp': timestamp  # 记录平仓时间
            })
            self.balance -= fee
            self.short_position = 0
            self.short_position_price = 0
            self.short_margin = 0

    def check_stop_loss_take_profit(self, price, timestamp):
        # 确保 history 不为空且最后一个记录有止损/止盈价格
        if not self.history or 'stop_loss_price' not in self.history[-1] or 'take_profit_price' not in self.history[-1]:
            return

        last_record = self.history[-1]
        stop_loss_price = last_record['stop_loss_price']
        take_profit_price = last_record['take_profit_price']

        # 检查多头止损止盈
        if self.long_position > 0:
            if price <= stop_loss_price:  # 触发止损
                self.close_long(price, timestamp, '止损')
            elif price >= take_profit_price:  # 触发止盈
                self.close_long(price, timestamp, '止盈')

        # 检查空头止损止盈
        if self.short_position > 0:
            if price >= stop_loss_price:  # 触发止损
                self.close_short(price, timestamp, '止损')
            elif price <= take_profit_price:  # 触发止盈
                self.close_short(price, timestamp, '止盈')

    def get_history(self):
        return pd.DataFrame(self.history)

    def analyze_trades(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = f"result/{timestamp}"
        os.makedirs(save_dir, exist_ok=True)

        history_df = self.get_history()
        history_df.to_csv(f"{save_dir}/trade.csv", index=False)

        with open(f"{save_dir}/analysis.txt", "w", encoding="utf-8") as f:
            f.write("交易分析报告\n")
            f.write("----------------------\n")
            f.write(f"初始资金: {self.initial_balance}\n")
            f.write(f"最终资金: {self.balance}\n")
            f.write(f"总收益: {self.balance - self.initial_balance}\n")

            total_trades = len(history_df[(history_df['type'] == 'close_long') | (history_df['type'] == 'close_short')])
            long_wins = len(history_df[(history_df['type'] == 'close_long') & (history_df['profit'] > 0)])
            short_wins = len(history_df[(history_df['type'] == 'close_short') & (history_df['profit'] > 0)])
            win_rate = (long_wins + short_wins) / total_trades if total_trades > 0 else 0

            f.write(f"总交易次数: {total_trades}\n")
            f.write(f"多头盈利次数: {long_wins}\n")
            f.write(f"空头盈利次数: {short_wins}\n")
            f.write(f"胜率: {win_rate:.2%}\n")
            back_result.openWeb(f"{save_dir}/trade.csv", port=5000)