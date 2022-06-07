# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 22:20:00 2022

@author: 1
"""

import pandas as pd
import sqlite3
from datetime import datetime
import os
import sched,time

url='https://data.ntpc.gov.tw/api/datasets/71CD1490-A2DF-4198-BEF1-318479775E8A/csv/file'

df=pd.read_csv(url)

def convert_time(date):
    return '-'.join([date[:4],date[4:6],date[6:8]])+' '+':'.join([date[8:10],date[10:12],date[12:]])

df['mday']=df['mday'].astype(str).apply(convert_time)
df1=df[['mday','sno','sna','sarea','ar','tot','sbi','bemp','act']]

conn=sqlite3.connect('ubike.db')
cursor=conn.cursor()
sqlstr='''
    create table if not exists data(
    mday datetime,
    sno integer,
    sna text,
    sarea text,
    ar text,
    tot integer,
    sbi integer,
    bemp integer,
    act integer
    );

    '''
cursor.execute(sqlstr)
conn.commit()

df1=df[['mday','sno','sna','sarea','ar','tot','sbi','bemp','act']]
df1.to_sql('data',conn,if_exists='append',index=False)

def get_youbike_tosql(sec=None,s=None):
    print(datetime.now())      
    df1=None
    if os.path.exists('temp.csv'):
        df1=pd.read_csv('temp.csv',index_col=0)    
    try:
        df=pd.read_csv(url)
        if not df.equals(df1):        
            # 資料是否重複
            df.to_csv('temp.csv')        
            df['mday']=df['mday'].astype(str).apply(convert_time)
            df1=df[['mday','sno','sna','sarea','ar','tot','sbi','bemp','act']]

            conn=sqlite3.connect('ubike.db')
            df1.to_sql('data',conn,if_exists='append',index=False)
            conn.close()
            print('write db.')            
        if s:
            s.enter(sec,0,get_youbike_tosql,argument=(sec,s))
    except Exception as e:
        print(e)  

s=sched.scheduler(time.time,time.sleep)
sec=3
s.enter(0,0,get_youbike_tosql,argument=(sec,s))
s.run()