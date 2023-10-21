# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 13:39:23 2023

3 kine test


@author: GTong
"""
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os

csv_file_path = 'D:/李老師/trade/result_data_test.txt'
data = pd.read_csv(csv_file_path)
# print(data.iloc[0, :])  # Print the first row

data_time = []
trade_price = []
_1min_k = []
profit_history = []
position_list = []
# 取出 time, price
data = pd.read_csv(csv_file_path)
data_time = data.iloc[:, 0].tolist()
trade_price = data.iloc[:, 1].tolist()


# 將輸入price/100原本API價格為實際的100倍
for i in range(len(trade_price)):
    trade_price[i] = trade_price[i] / 100


# print(data_time[0][0:16])

# 計算分鐘K (一分鐘內最大值與最小值) 使用trade_price換算
def cac_Kline():
    Kmax = 0
    Kmin = 100000
    Kline_close_time = ''    
    for i  in range(len(trade_price)):
        if(i == 0):
            print("Start creat 1 min kline")
            print("First time at: "+str(data_time[0][0:16]))
            Kline_close_time = data_time[0][0:16]
        
        elif(Kline_close_time != data_time[i][0:16]):
            k_data = []
            k_data.append(Kline_close_time)
            k_data.append(Kmax)
            k_data.append(Kmin)
            _1min_k.append(k_data)
            Kmax = 0
            Kmin = 100000
            print(data_time[i][0:16])
        Kmax = max(Kmax,trade_price[i])
        Kmin = min(Kmin,trade_price[i])
        Kline_close_time = data_time[i][0:16]
    print(_1min_k)        # example: _1min_k[1] = ['2023-09-12 20:01', 16549.0, 16548.0] -> [time, high, low]
    # print(_1min_k)
    # print(data_time)

def trade_index(times):  # 輸入目前index，回傳做多 or 做空 or 不動作
    k1 = []
    k2 = []
    window_dir = 3 # k棒趨勢
    index = 2  # 回傳交易方向 0:做空、1:做多、2:不動作
    upper = 0  # windows size
    lower = 0  # windows size
    now_price = trade_price[times]
    for i in range(len(_1min_k)):
        if(data_time[times][0:16] == _1min_k[i][0]): #找到前2mins Kline
            k1 = _1min_k[i-2]
            k2 = _1min_k[i-1]
            if(k2[1] > k1[1] and k2[2] > k1[2]):     # K2最大值大於K1，K2最小值大於K2 (Kline higher hight)上升趨勢
                window_dir = 1 #做多，先買後賣
                upper = (k2[1] - k1[1]) / 600 * float(data_time[times][17:21])*10 + k2[1] 
                lower = (k2[2] - k1[2]) / 600 * float(data_time[times][17:21])*10 + k2[2] 
            elif(k2[1] < k1[1] and k2[2] < k1[2]):   # K2最大值小於K1，K2最小值小於K2 (Kline lower to low)下降趨勢
                window_dir = 0 #做空，先賣後買
                upper = (k2[1] - k1[1]) / 600 * float(data_time[times][17:21])*10 + k2[1] 
                lower = (k2[2] - k1[2]) / 600 * float(data_time[times][17:21])*10 + k2[2]
            
            break 
    if(now_price < lower and window_dir == 1): # 上升趨勢，但價格跌破低點
        # print("做多")
        index = 1
    elif(now_price > upper and window_dir == 0): # 下降趨勢，但價格漲過高點
        # print("做空")
        index = -1
        
    return 2 if(k1 == [] or k2 == [] or  window_dir == 3) else index # 回傳交易方向




def stop_position(time_str):  # 如果時間在  09:10~13:20 16:10~03:30 return 1 else return 0
    # 將時間字串分割成小時和分鐘
    time_str = time_str[11:16]
    hour, minute = map(int, time_str.split(":"))
    
    # 將小時和分鐘轉換為一天中的總分鐘數
    total_minutes = hour * 60 + minute
    
    # 計算時間範圍的總分鐘數
    morning_start = 9 * 60 + 10
    morning_stop_trade = 13 * 60 - 30 # 12:30後不開倉
    morning_end = 13 * 60 + 20
    evening_start = 16 * 60 + 10
    evening_stop_trade = 3 * 60 - 30 # 2:30後不開倉
    evening_end = 3 * 60 + 30
    
    # 檢查時間是否在範圍內
    if morning_start <= total_minutes <= morning_stop_trade:
        return 1
    if evening_start <= total_minutes or total_minutes <= evening_stop_trade:
        return 1
    if morning_start <= total_minutes <= morning_end:
        return 2
    if evening_start <= total_minutes or total_minutes <= evening_end:
        return 2
    
    return 0
    
def save_result(start_time,end_time,trade_time,long_postion_times,short_postion_times,stop_profit_times,stop_loss_times,
                Next_day_clean_times,profit,net_profit,execution_time,profit_history,backtrace_parameter):
    with open('D:/李老師/trade/data/'+str(backtrace_parameter)+'.json', 'w') as f:
        json.dump({'start_time': start_time, 'end_time': end_time, 'trade_time': trade_time, 
                   'long_postion_times': long_postion_times, 'short_postion_times': short_postion_times, 
                   'stop_profit_times': stop_profit_times, 'stop_loss_times': stop_loss_times, 'Next_day_clean_times': Next_day_clean_times, 
                   'profit': profit, 'net_profit': net_profit, 'execution_time': execution_time, 'profit_history': profit_history, 
                   'backtrace_parameter': backtrace_parameter}, f)

    
def backtrace(stop_profit, stop_loss):
    start = time.time() # 計算程式執行時間
    cac_Kline()
    profit = 0
    profit_history.clear()
    position_list.clear()
    stop_profit_times = 0 # 停利次數
    stop_loss_times = 0 # 停損次數
    Next_day_clean_times = 0 # 隔日清倉次數
    long_postion_times = 0 # 多倉開倉次數
    short_postion_times = 0 # 空倉開倉次數
    direction = 1 # -1:作空 1:作多
    open_position_price = 0 # 開倉價格
    trade_time = 0 # 開倉次數
    last_opening_time = "00:00"
    backtrace_parameter = str(stop_profit)+'~'+str(stop_loss) # "50~-50"
    for times in range(len(trade_price)):         
        now_price = trade_price[times] # 目前價格
        index = trade_index(times) # 回傳交易方向 range
        allowTrade = stop_position(data_time[times]) 
        
        if(allowTrade == 0):
            print("隔時段平倉")
            for i in reversed(range(len(position_list))):
                temp_profit = (now_price - position_list[i][0]) * position_list[i][1] # 倉位獲利
                profit += temp_profit
                del position_list[i]  # 刪除索引為 i 的元素
                Next_day_clean_times += 1
        
        for i in reversed(range(len(position_list))):
            temp_profit = (now_price - position_list[i][0]) * position_list[i][1] # 倉位獲利
            print(temp_profit)
            if(temp_profit > stop_profit): # 停利倉位
                print("倉位停利---------------------------------------------------")
                stop_profit_times += 1
                profit += temp_profit
                del position_list[i]  # 刪除索引為 i 的元素
            elif(temp_profit < stop_loss):
                print("倉位停損----------------------------------------------------")
                stop_loss_times += 1
                profit += temp_profit
                del position_list[i]  # 刪除索引為 i 的元素
                
        if(index != 2 and last_opening_time != data_time[times][11:16] and allowTrade == 1): #開倉判斷
            last_opening_time = data_time[times][11:16] # 更新開倉時間
            position_temp = [now_price,index] # example : [16827.0, -1]
            position_list.append(position_temp)
            trade_time += 1
            if(index == 1):
                long_postion_times += 1
            else:
                short_postion_times += 1


        # print("目前平倉獲利:"+str(profit))
        if(times == len(trade_price)-1):
            print("回測結束")
            for i in reversed(range(len(position_list))):
                temp_profit = (now_price - position_list[i][0]) * position_list[i][1] # 倉位獲利
                profit += temp_profit
                del position_list[i]  # 刪除索引為 i 的元素
                Next_day_clean_times += 1
            
        profit_history.append(profit)
    # print(lisa)
    # print(profit)
    end = time.time()
    print("start date: "+str(data_time[0]))
    print("end date: "+str(data_time[-1]))
    print("回測參數: "+backtrace_parameter)
    print("開倉次數: "+str(trade_time))
    print("多倉次數: "+str(long_postion_times))
    print("空倉次數: "+str(short_postion_times))
    print("停利次數: "+str(stop_profit_times))
    print("停損次數: "+str(stop_loss_times))
    print("隔日清倉次數: "+str(Next_day_clean_times))
    print("獲利: "+str(profit))
    print("淨獲利: "+str(profit-trade_time*2))
    print("回測花費時間: %f 秒" % (end - start))
    
    # save_result(str(data_time[0]),str(data_time[-1]),str(trade_time),str(long_postion_times),str(short_postion_times),str(stop_profit_times),str(stop_loss_times),
                # str(Next_day_clean_times),str(profit),str(profit-trade_time*2),str((end - start)),profit_history,backtrace_parameter)


def plot_profit_history():
    x_indices = list(range(len(profit_history)))
    # 繪製圖表
    plt.figure(figsize=(8, 6))  # 設定圖表大小
    plt.plot(x_indices, profit_history, marker='.')  # 繪製數據，'o' 代表使用圓點標記
    plt.title('profit curve')  # 設定標題
    plt.xlabel('times')  # 設定 x 軸標籤
    plt.ylabel('profit')  # 設定 y 軸標籤
    plt.grid(True)  # 顯示網格
    plt.show()  # 顯示圖表

    

def loop_back_trace():
    for i in range(10, 101, 10):
        for j in range(10, 101, 10):
            backtrace(i, j*-1)


def read_All_file_profit():
    # 設定要讀取的資料夾路徑
    folder_path = 'data/'

    # 獲取資料夾中的所有檔案名稱
    file_names = os.listdir(folder_path)
    
    # 遍历所有檔案
    for file_name in file_names:
        
        # 檢查是否為JSON檔案
        if file_name.endswith('.json'):
            
            # 組合完整的檔案路徑
            full_file_path = os.path.join(folder_path, file_name)
        
            # 讀取JSON檔案
            with open(full_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                profit = data['profit']
                net_profit = data['net_profit']
                backtrace_parameter = data['backtrace_parameter']
                print('backtrace_parameter: '+str(backtrace_parameter)+'  profit: '+str(profit)+'  net_profit: '+str(net_profit))
     
    
    
def plot_profit_and_price(backtrace_parameter):
    
    flie_path = 'data/'+str(backtrace_parameter)+'.json'
    # trade_price
    with open(flie_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        profit_history = data['profit_history']
        backtrace_parameter = data['backtrace_parameter']
    
    # 創建一個figure和一個axes（子圖）
    fig, ax1 = plt.subplots()

    # 繪製第一個list並設定軸刻度和標籤
    ax1.plot(trade_price, 'b-', label='List 1')
    ax1.set_xlabel('time')
    ax1.set_ylabel('price', color='b')
    ax1.tick_params('y', colors='b')
    
    # 使用twinx創建第二個y軸
    ax2 = ax1.twinx()
    
    # 繪製第二個list並設定軸刻度和標籤
    ax2.plot(profit_history, 'r-', label='List 2')
    ax2.set_ylabel('profit', color='r')
    ax2.tick_params('y', colors='r')

    # 顯示圖表
    plt.show()
