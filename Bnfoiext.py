
''''
This program is to extract BANKNIFTY Option Chain data from NSE website
by using MongoDB
This script also shows charts for strike prices upon timestamp

'''

import requests
import pandas as pd
from datetime import datetime
import json
from pymongo import MongoClient
import time

def main():
    '''
     Method main
    '''
    Start_Time = time.time()
    cNt = 0
    while datetime.now().strftime("%H:%M:%S") < '15:30:30':
        try:
            headerU = {'User-Agent': "Mozilla/5.0 \
                  (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                  (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"}
            url1 = "https://www.nseindia.com/live_market/dynaContent\
                /live_watch/option_chain/\
                 optionKeys.jsp?symbolCode=-9999&symbol=\
                  BANKNIFTY&symbol=BANKNIFTY&instrument=OPTIDX&date\
                   =-&segmentLink=17&segmentLink=17"
            idata2 = pd.read_html(requests.get(url1, headers=headerU).content)[0].loc[0, 1]
            idata = pd.read_html(requests.get(url1, headers=headerU).content)[1]
        except:
            print("Error...!!!")
            time.sleep(15)
        #idata = idata().apply(pd.to_numeric)
        strp = idata.loc[:, ('Unnamed: 11_level_0')]
        strp = strp['Strike Price'].fillna(0).astype('int')
        #[int(i) for i in strp]
        cdf = idata.loc[:, ('CALLS')]
        cdf = cdf.drop(['Chart', 'BidQty', 'BidPrice', 'AskPrice', 'AskQty'], 1)
        pdf = idata.loc[:, ('PUTS')]
        pdf = pdf.drop(['Chart', 'BidQty', 'BidPrice', 'AskPrice', 'AskQty'], 1)
        cdf.columns = ['CALL_OI', 'Chg_CallOI', 'CALL_Volume', 'CALL_IV', 'CALL_LTP', 'CALL_LTPChg']
        pdf.columns = ['PUT_LTPChg', 'PUT_LTP', 'PUT_IV', 'PUT_Volume', 'Chg_PutOI', 'PUT_OI']
        spot = idata2.split(" ").pop(3) #spot price
        timeStamp = idata2.split(" ").pop(9) #time
        Date1 = idata2.split(" ").pop(6)+' ' +idata2.split(" ").pop(7)+' '+ \
                                            idata2.split(" ").pop(8) #Date
        mspot = round(float(spot), -2)
        mspot = int(mspot) # round and int spot strike
        date2 = datetime.strptime(Date1, '%b %d, %Y')
        Date = date2.date()
        mdf = pd.merge(cdf, pdf, left_index=True, right_index=True)
        dt = pd.DataFrame([Date] * len(strp))
        ts = pd.DataFrame([timeStamp] * len(strp))
        spt = pd.DataFrame([spot] * len(strp))
        strTs = pd.concat([ts, strp], axis=1).dropna(how='any')
        strTs.rename(columns={0:'TimeStamp', 'Strike Price':'StrikePrice'}, inplace=True)
        spt.rename(columns={0:'Spot'}, inplace=True)
        dt.rename(columns={0:'Date'}, inplace=True)
        #Add Dataframes strTs and mdf and set strTs as MultiIndex
        mdf = pd.concat([strTs, spt, mdf], axis=1).dropna(how='any').set_index(['TimeStamp', \
                     'StrikePrice', 'Spot'])
        mdf.replace('-', 0, inplace=True)
        mdfi = mdf.reset_index()
        mdfi[['CALL_OI', 'Chg_CallOI', 'CALL_Volume', 'PUT_Volume', 'Chg_PutOI', 'PUT_OI']] = \
        mdfi[['CALL_OI', 'Chg_CallOI', 'CALL_Volume', 'PUT_Volume', 'Chg_PutOI', 'PUT_OI']] \
        .astype('int')
        mdfi[['Spot', 'CALL_LTP', 'CALL_LTPChg', 'CALL_IV', 'PUT_LTPChg', 'PUT_LTP', 'PUT_IV']] = \
        mdfi[['Spot', 'CALL_LTP', 'CALL_LTPChg', 'CALL_IV', 'PUT_LTPChg', 'PUT_LTP', 'PUT_IV']] \
        .astype('float')
        try:
            conne = MongoClient()
            cNt += 1
            print("Connected successfully!!! ", cNt, datetime.now().strftime("%H:%M:%S"), timeStamp)
        except:
            print("Could not connect to MongoDB")
        db = conne.bnf0220
        rec = json.loads(mdfi.T.to_json()).values()
        db.myCollection.insert_many(rec)
        collection = db.myCollection
        #Date = datetime.date(datetime.now())
        #collection = db.myCollection
        d = pd.DataFrame(list(collection.find()))
        d = d.drop(['_id'], 1)
        #d.apply(pd.to_numeric(d, downcast='unsigned'))
        #d[['TimeStamp']]=d[['TimeStamp']].astype('datetime')
        d.to_excel(r'C:\Users\c.kilari\Desktop\BNF0220.xlsx', sheet_name='BNF0220')
        time.sleep(150.0 - ((time.time() - Start_Time) % 150.0))

    print('Market is closed..come tomorrow!!')

main()
'''
End

'''
