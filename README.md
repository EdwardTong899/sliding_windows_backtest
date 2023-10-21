# Sliding windows trading backtest

 
   - 使用多個1分k棒的最高點與最低點連線形成趨勢，當趨勢向上但價格跌破低點就做多，反之做空
   - 使用BFS策略，當有訊號時就會建立一個倉位，可更公平的評估有效性
   - 只在特定時間內建立倉位，避免在交易截止時間前開倉

# 執行流程
1. 讀取tick時間資料
   - csv_file_path = 'D:/李老師/trade/result_data_test.txt'
  
2. 組成1分K
       - example: _1min_k[1] = ['2023-09-12 20:01', 16549.0, 16548.0] -> [time, high, low]

```shell
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
```  

3. 判斷交易時間
    - 當時間為交易時間時回傳1，交易時間但靠近收盤時間時回傳2，非交易時間回傳0
```shell
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
```  
4. 主程式執行 def backtrace(stop_profit, stop_loss)
       - 輸入停利價格與停損價格 ex: backtrace(50, -50)就可以調用以上程式開始跑回測 
       - 輸出格式 start date: 2023-09-12 20:01:37.117 
       - end date: 2023-09-13 09:19:26.524 
       - 回測參數: 10~-10 
       - 開倉次數: 131 
       - 多倉次數: 69 
       - 空倉次數: 62 
       - 停利次數: 28 
       - 停損次數: 40 
       - 隔日清倉次數: 63 
       - 獲利: -133.0 
       - 淨獲利: -395.0 # 扣除開倉手續費 
       - 回測花費時間: 4.542853 秒 # 程式執行時間 















