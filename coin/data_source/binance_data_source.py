import os
import csv

import pandas as pd
from binance.um_futures import UMFutures
from datetime import datetime
from tqdm import tqdm

# 初始化 Binance UM Futures 客户端
um_futures_client = UMFutures()


def save_data_to_csv(symbol, interval, data):
    """将数据保存到 CSV 文件并返回 DataFrame"""
    folder = f'kline/{symbol}/{interval}'
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = f'{folder}/{symbol}_{interval}.csv'

    # 定义表头与数据字段对应关系
    header = [
        'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close Time', 'Quote Volume', 'Number of Trades',
        'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
    ]

    # 写入文件（首次写入时包含表头）
    file_exists = os.path.exists(file_path)
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)
    print(f"数据已保存至 {file_path}")

    # 将数据转换为 DataFrame
    df = pd.DataFrame(data, columns=header)
    return df


def load_existing_data(symbol, interval):
    """加载本地存储的 K 线数据并转换数据类型"""
    file_path = f'kline/{symbol}/{interval}/{symbol}_{interval}.csv'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # 跳过表头
            data = []
            for row in reader:
                # 数据类型转换（与Binance API返回格式一致）
                converted = [
                    int(row[0]),  # Open Time (timestamp)
                    row[1],  # Open
                    row[2],  # High
                    row[3],  # Low
                    row[4],  # Close
                    row[5],  # Volume
                    int(row[6]),  # Close Time (timestamp)
                    row[7],  # Quote Volume
                    int(row[8]),  # Number of Trades
                    row[9],  # Taker Buy Base
                    row[10],  # Taker Buy Quote
                    row[11]  # Ignore
                ]
                data.append(converted)
        return data
    return []


def get_kline_data(symbol, interval, total_bars):
    """获取 K 线数据（自动合并本地与远程数据）"""
    # 加载本地数据
    existing_data = load_existing_data(symbol, interval)

    # 如果本地数据充足则直接返回
    if len(existing_data) >= total_bars:
        print(f"本地数据充足（{len(existing_data)}条），直接使用缓存")
        return existing_data[-total_bars:]  # 返回最新的指定条数

    # 计算需要获取的数据量
    need_fetch = total_bars - len(existing_data)
    all_data = []
    end_time = None

    # 进度条设置
    with tqdm(total=need_fetch, desc=f"下载 {symbol} {interval} 数据") as pbar:
        while need_fetch > 0:
            # 计算本次请求的条数（最大1000）
            limit = min(need_fetch, 1000)

            # 获取历史数据（end_time用于分页）
            params = {'symbol': symbol, 'interval': interval, 'limit': limit}
            if end_time:
                params['endTime'] = end_time

            response = um_futures_client.klines(**params)
            if not response:
                break

            # 更新数据与进度条
            all_data = response + all_data  # 保证时间顺序
            fetched = len(response)
            need_fetch -= fetched
            pbar.update(fetched)

            # 更新下一次请求的结束时间
            end_time = response[0][0] - 1  # 使用第一条数据的时间戳前移1ms

    # 合并新旧数据并排序
    merged_data = all_data + existing_data
    merged_data.sort(key=lambda x: x[0])  # 按开盘时间排序

    # 保存合并后的数据
    return save_data_to_csv(symbol, interval, merged_data[-total_bars:])  # 保留最新指定条数


# 示例用法
if __name__ == "__main__":
    data = get_kline_data("BTCUSDT", "5m", 50000)
    print(data)