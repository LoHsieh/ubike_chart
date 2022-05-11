# -*- coding: utf-8 -*-
"""
Created on Tue May 10 17:35:39 2022

@author: 1
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from copy import deepcopy

conn=sqlite3.connect('mydb.db')
df=pd.read_sql_query('select * from youbike_data',con=conn)
conn.close()

df=df.drop(df[df['act']==0].index)
df.drop_duplicates(inplace=True)

ubike=deepcopy(df)
ubike['date']=pd.to_datetime(ubike['date'])
ubike=ubike.sort_values('date').set_index('date')

ubike_0317=ubike.loc['2021-3-17'].dropna()
df_sna=ubike_0317.groupby('sna').get_group('漳和國中')
df_30min=df_sna.resample('30min').mean()[['tot','sbi','bemp']].dropna().round().astype(int)

# df_30min[['sbi','bemp']].plot(kind='bar',figsize=(12,6))
# plt.show()

date=df_30min.index[0].strftime('%Y-%m-%d')
mean=round(df_30min['sbi'].mean())

x=df_30min.index.strftime('%H:%M')

plt.figure(figsize=(12,6))

sna='Xizhi Station'
plt.bar(x,df_30min['bemp'],color='#205375',label='unavailable')
plt.bar(x,df_30min['sbi'],color='#F66B0E',label='available')
plt.plot(x,[mean]*len(df_30min),'--r',label='average',color='#EEEEEE')

# plt.xlabel('time',labelpad=12,fontsize=18)
plt.ylabel('bikes',labelpad=12,fontsize=18)

plt.xlim(-1,len(df_30min))
plt.legend()
plt.xticks(rotation=90)

max_y=df_30min['bemp'].max()+3
# 文字顯示部分
plt.text(-1.0,max_y+0.5,f'{date} {sna}  (total:{df_30min["tot"].max()} average:{mean})',fontsize=22)

plt.text(len(df_30min)+1,max_y,'peak hours',fontsize=16)
plt.text(len(df_30min)+5,max_y,'off-peak hours',fontsize=16)

for i,time in enumerate(df_30min[df_30min['sbi']==0].index.strftime('%H:%M')):
    plt.text(len(df_30min)+1,max_y-3.5-i*3,time,fontsize=16,color='#F66B0E')
    
for i,time in enumerate(df_30min[df_30min['sbi']>=mean].index.strftime('%H:%M')):
    plt.text(len(df_30min)+5,max_y-3.5-i*3,time,fontsize=16,color='#205375')
    
plt.savefig(f'{sna}.png',bbox_inches='tight')

plt.show()