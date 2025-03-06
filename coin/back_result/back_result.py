from flask import Flask, render_template
import pandas as pd
import logging
import webbrowser
import threading

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.DEBUG)

# 从 CSV 文件读取数据
def load_data_from_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        logging.error(f"文件 {file_path} 未找到！")
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"加载数据时出错: {e}")
        return pd.DataFrame()

# 计算交易指标
def calculate_metrics(df):
    if df.empty:
        return {
            "win_rate": 0,
            "total_profit": 0,
            "profit_factor": 0,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "avg_holding_time": 0,
            "equity_curve": [{"timestamp": None, "balance": 0}],
            "max_drawdown": 0,
            "long_winning_trades": 0,
            "short_winning_trades": 0,
            "total_fee": 0
        }

    # 确保必要的列存在，如果不存在则填充默认值
    required_columns = ['type', 'profit', 'fee', 'timestamp', 'balance']
    for col in required_columns:
        if col not in df:
            df[col] = 0 if col != 'timestamp' else pd.Timestamp('1970-01-01')

    # 填充空的 profit 和 balance 为 0
    df['profit'] = df['profit'].fillna(0)
    df['balance'] = df['balance'].fillna(0)

    # 计算空头交易指标
    short_trades = df[df['type'] == 'close_short']
    total_short_trades = len(short_trades)
    short_winning_trades = len(short_trades[short_trades['profit'] > 0])
    short_losing_trades = len(short_trades[short_trades['profit'] < 0])

    # 计算多头交易指标
    long_trades = df[df['type'] == 'close_long']
    total_long_trades = len(long_trades)
    long_winning_trades = len(long_trades[long_trades['profit'] > 0])
    long_losing_trades = len(long_trades[long_trades['profit'] < 0])

    # 总交易次数
    total_trades = total_short_trades + total_long_trades
    winning_trades = short_winning_trades + long_winning_trades
    losing_trades = short_losing_trades + long_losing_trades

    # 胜率
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

    # 总利润
    total_profit = short_trades['profit'].sum() + long_trades['profit'].sum()

    # 盈亏比
    total_winning_profit = short_trades[short_trades['profit'] > 0]['profit'].sum() + long_trades[long_trades['profit'] > 0]['profit'].sum()
    total_losing_profit = abs(short_trades[short_trades['profit'] < 0]['profit'].sum() + long_trades[long_trades['profit'] < 0]['profit'].sum())
    profit_factor = total_winning_profit / total_losing_profit if total_losing_profit > 0 else 0

    # 计算平均持仓时间（单位：分钟）
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', errors='coerce')
    df['holding_time'] = df.groupby((df['type'].isin(['buy', 'sell'])).cumsum())['timestamp'].diff()
    avg_holding_time = df[df['type'].isin(['close_long', 'close_short'])]['holding_time'].mean()
    avg_holding_time = avg_holding_time.total_seconds() / 60 if pd.notna(avg_holding_time) else 0

    # 计算资金曲线（仅使用 close_long 和 close_short 的 balance）
    closed_trades = df[df['type'].isin(['close_long', 'close_short'])].copy()
    equity_curve = closed_trades[['timestamp', 'balance']].to_dict('records')
    if not equity_curve:
        equity_curve = [{"timestamp": None, "balance": 0}]

    # 计算最大回撤（基于 balance）
    if not closed_trades.empty and closed_trades['balance'].max() > 0:
        max_drawdown = ((closed_trades['balance'].max() - closed_trades['balance'].min()) / closed_trades['balance'].max()) * 100
    else:
        max_drawdown = 0

    # 计算总手续费
    total_fee = df['fee'].sum()

    return {
        "win_rate": win_rate,
        "total_profit": total_profit,
        "profit_factor": profit_factor,
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "avg_holding_time": avg_holding_time,
        "equity_curve": equity_curve,
        "max_drawdown": max_drawdown,
        "long_winning_trades": long_winning_trades,
        "short_winning_trades": short_winning_trades,
        "total_fee": total_fee
    }

# 定义全局变量，用于存储 trades 和 metrics
global_trades = None
global_metrics = None
global_profits = None
global_equity_curve = None

@app.route('/')
def index():
    global global_trades, global_metrics, global_profits, global_equity_curve
    return render_template(
        'index.html',
        table=global_trades,
        metrics=global_metrics,
        profits=global_profits,
        equity_curve=global_equity_curve
    )

def openWeb(csv_path, port=5000):
    """
    启动 Flask Web 应用，并自动打开浏览器
    :param csv_path: CSV 文件路径
    :param port: 端口号，默认为 5000
    """
    global global_trades, global_metrics, global_profits, global_equity_curve

    # 加载数据
    df = load_data_from_csv(csv_path)
    if df.empty:
        logging.error("加载的数据为空，无法启动 Web 应用！")
        return

    # 计算指标
    metrics = calculate_metrics(df)

    # 将 df 转换为字典列表，并处理时间戳
    trades = df.to_dict('records')
    for trade in trades:
        if pd.isna(trade['timestamp']):
            trade['timestamp'] = None
        else:
            trade['timestamp'] = pd.Timestamp(trade['timestamp'], unit='ms').strftime('%Y-%m-%d %H:%M:%S') if trade['timestamp'] else None
        trade['profit'] = trade['profit'] if pd.notna(trade['profit']) else 0
        trade['balance'] = trade['balance'] if pd.notna(trade['balance']) else 0

    # 分配全局变量
    global_trades = trades
    global_metrics = metrics
    global_profits = df[df['type'].isin(['close_long', 'close_short'])]['profit'].fillna(0).tolist()
    global_equity_curve = metrics['equity_curve']

    # 自动打开浏览器
    url = f'http://127.0.0.1:{port}'
    threading.Timer(1, lambda: webbrowser.open(url)).start()

    # 启动 Flask 应用
    app.run(debug=True, port=port, use_reloader=False)

