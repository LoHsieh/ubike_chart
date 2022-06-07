# -*- coding: utf-8 -*-
"""
Created on Tue May 10 17:35:39 2022

@author: 1
"""

import pandas as pd
from sqlite3 import connect
import matplotlib.pyplot as plt
from copy import deepcopy
import os

with connect('mydb.db') as conn:
    df=pd.read_sql('SELECT * FROM youbike_data',con=conn)

df.drop_duplicates(inplace=True)
df=df.drop(df[df['act']==0].index) # act車站使用情況 1=運作中 0=暫停使用

ubike=deepcopy(df).dropna()
ubike['date']=pd.to_datetime(ubike['date'])
ubike=ubike.sort_values('date').set_index('date')

#設定圖表字體 尺寸
plt.rcParams['font.sans-serif'] = ['Taipei Sans TC Beta']
plt.figure(figsize=(12,6))

sna_list=ubike.groupby('sna').size().index

#迴圈設定站點及日期變數
for sna in sna_list:
    temp_sna=ubike.groupby('sna').get_group(sna)
    temp_sna_re=temp_sna.resample('D')
    
    for raw_date in temp_sna_re.size().index:
        sna_date=raw_date.strftime('%Y-%m-%d')
        ubike_temp_date=ubike.loc[sna_date]
        df_sna=ubike_temp_date.groupby('sna').get_group(sna)
        df_30min=df_sna.resample('30min').mean()[['tot','sbi','bemp']].dropna().astype(int)
        
        mean=round(df_30min['sbi'].mean())

        x=df_30min.index.strftime('%H:%M')

        plt.bar(x,df_30min['bemp'],color='#205375',label='unavailable')
        plt.bar(x,df_30min['sbi'],color='#F66B0E',label='available')
        plt.plot(x,[mean]*len(df_30min),'--r',label='average',color='#EEEEEE')

        plt.ylabel('number of bikes',labelpad=12,fontsize=18)

        plt.xlim(-1,len(df_30min))
        plt.legend()
        plt.xticks(rotation=90)

        # 文字顯示部分
        unit_y=([
                 df_30min['sbi'].max() 
                 if df_30min['sbi'].max()>df_30min['bemp'].max() 
                 else df_30min['bemp'].max()
                ][0]//5+1)
        plt.text(-1,unit_y*5.2,
                 f'{sna_date} {sna}  (total:{df_30min["tot"].max()} average:{mean})',
                 fontsize=22)

        plt.text(len(df_30min)+1,unit_y*5.2,'peak hours',fontsize=16)
        plt.text(len(df_30min)+5,unit_y*5.2,'off-peak hours',fontsize=16)

        for i,time in enumerate(df_30min[
                                         df_30min['sbi'] < (df_30min['tot']*0.2)
                                        ].index.strftime('%H:%M')):
            plt.text(len(df_30min)+1,unit_y*4.8-i*unit_y*0.3,time,fontsize=16,color='#F66B0E')

        for i,time in enumerate(df_30min[
                                         df_30min['sbi'] >= (df_30min['tot']*0.7)
                                        ].index.strftime('%H:%M')):
            plt.text(len(df_30min)+5,unit_y*4.8-i*unit_y*0.3,time,fontsize=16,color='#205375')

        if not os.path.exists(sna_date):
            os.makedirs(sna_date)
        plt.savefig(f'{sna_date}/{sna}.png',bbox_inches='tight')
        plt.cla()
print('done!')