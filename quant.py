import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  
from pandas import Series,DataFrame
from datetime import timedelta,date
import seaborn as sns
sns.set_style('white')

start = '20120101'                       # 回测起始时间
end =   '20160111'                         # 回测结束时间
benchmark = 'HS300'                        # 策略参考标准
#benchmark = '399006.ZICN'
universe = ['159915.XSHE']  # 证券池，支持股票和基金
#universe = ['510300.XSHG'] 
#universe = ['510050.XSHG'] 
commission = Commission(0.0,0.0)

capital_base = 100000                      # 起始资金
freq = 'd'                                 # 策略类型，'d'表示日间策略使用日线回测，'m'表示日内策略使用分钟线回测
refresh_rate = 1                           # 调仓频率，表示执行handle_data的时间间隔，若freq = 'd'时间间隔的单位为交易日，若freq = 'm'时间间隔为分钟

#self defined data
#最优参数，ma_short=8 ma_long=26;当开盘MA3和MA23金叉时买入，MA3和MA23死叉时卖出

#(3 20) (5 21)
window_short = 3
window_long = 20
#switch 
StopLoss_on = 1
#BuyStep_on = 1  #BuyStep=0 采用单次建仓
universe_tuple = tuple(universe)


global high_price,now_value,flag
global approximationAmount,b1st_price,avg_price
high_price =0
flag = 1
BuyStep = 0  #第一次买入1/3；第二次买入1/3,当价格比第一次买入价格涨BuyStep%买入；当价格再涨BuyStep%，第三次买入满仓；BuyStep=0 采用单次建仓
approximationAmount=0
b1st_price=0
stop_rate=90

def initialize(account):                   # 初始化虚拟账户状态
    pass

def handle_data(account):                  # 每个交易日的买入卖出指令
    hist = account.get_attribute_history('closePrice',window_long)
    etf = universe_tuple[0]
    today = account.current_date
    preday = today + timedelta(days = -100)
    yestoday = today + timedelta(days = -1)

    global high_price,now_value,flag
    global approximationAmount,b1st_price,avg_price


    cIndex = DataAPI.MktIdxdGet(ticker='399006',beginDate=preday,endDate=yestoday,field=["tradeDate","closeIndex"],pandas="1")
    maIndexShort  = np.round(pd.rolling_mean(cIndex['closeIndex'],window=window_short),2)
    maIndexLong  = np.round(pd.rolling_mean(cIndex['closeIndex'],window=window_long),2)
    filter_std = np.std(cIndex['closeIndex'][-window_long:],axis=0)  #not used
    curPosition = account.position.secpos.get(etf, 0)
    today_index = cIndex['closeIndex'].values[-1]
    #print today_index.values[-1]
    today_price = hist[universe_tuple[0]][-1]

    if maIndexShort.values[-1] > maIndexShort.values[-2]  and maIndexLong.values[-1] > maIndexLong.values[-2] and flag==1:
        now_value = account.position.secpos.get(etf, 0)*hist[universe_tuple[0]][-1]
        if curPosition == 0 :
            if BuyStep != 0 :
                approximationAmount = int(account.cash / (today_price*1.02)/1000.0) * 300
            else :
                approximationAmount = int(account.cash / (today_price*1.02)/100.0) * 100
            b1st_price = today_price
            avg_price = today_price
            print 
            order(universe_tuple[0],approximationAmount)
        elif curPosition == approximationAmount and  today_price > (1+BuyStep/100.0)*b1st_price and BuyStep !=0 :
            order(universe_tuple[0],approximationAmount) 
        elif curPosition == 2*approximationAmount and  today_price > (1+2*BuyStep/100.0)*b1st_price and BuyStep !=0 :
            lastAmount = int(account.cash / (today_price*1.02)/100.0) * 100
            #print 'lastAmount :{0:20d} m:{1:20d}'.format(lastAmount,account.position.secpos.get(etf, 0))
            high_value = (lastAmount+account.position.secpos.get(etf, 0))*today_price
            order(etf,lastAmount)  
        elif StopLoss_on ==1 and curPosition !=0:
            #print curPosition
            #分级移动止盈
            profit_level = high_price/avg_price-1
            if high_price < today_price :
                high_price = today_price
            if profit_level < 0.2 :
                stopLoss_price = high_price*0.7
            elif 0.2 <= profit_level < 0.5 :
                stopLoss_price = high_price*0.8
            elif profit_level >= 0.5 :
                stopLoss_price = high_price*0.9
            if today_price < stopLoss_price and flag!=0 :
                high_price = 0;
                flag =0
                print 'profit {0:>7.4} stoploss @ {1:>7.4}  '.format(profit_level,stopLoss_price)
                order_to(etf,0)
    elif maIndexShort.values[-1] < maIndexShort.values[-2] and maIndexLong.values[-1] < maIndexLong.values[-2]  :
        flag=1
        if account.position.secpos.get(etf, 0) > 0:
            order_to(etf,0)
    else :
        #if isnan(maIndexShort.values[-1]) or isnan(maIndexLong.values[-1]) :
        #    print 'Warning : MA is NaN.'
        pass


