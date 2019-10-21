from datetime import datetime
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from dateutil.parser import parse as parse_date
import os
#import nltk
import string
import config_indo as config
#import pickle
from sklearn.externals import joblib
import warnings


formatStr = '%Y%m%d%H%M%S'
def in_app_reviews_writeToES(f,logger):
    with open(config.object_ser_classifier_file, 'rb') as input:   
        classifier = joblib.load(input)
    df = pd.DataFrame()
    h, b = os.path.split(f)
    try:
        df = pd.read_csv(f, encoding='utf-16')
    except:
        df = pd.read_csv(f, encoding='ISO-8859-1')

    df.columns=['Package_Name','App_Version_Code','App_Version_Name','Reviewer_Lang',
                'Device','Review_Submit_Date_Time','Review_Submit_Millis_Since_Epoch','Review_Last_Update_Date_Time',
                'Review_Last_Update_Millis_Since_Epoch','Star_Rating','Review_Title','Review_Text',
                'Developer_Reply_Date_Time','Developer_Reply_Millis_Since_Epoch','Developer_Reply_Text','Review_Link']
     
    df1=df.select_dtypes(['object'])

    df[df1.columns]=df1.apply(lambda x: x.str.strip())
    
    df.Review_Submit_Date_Time=pd.to_datetime(df.Review_Submit_Date_Time,dayfirst = True,errors='ignore')
    df.Review_Last_Update_Date_Time=pd.to_datetime(df.Review_Last_Update_Date_Time,dayfirst = True,errors='ignore')
    df.Developer_Reply_Date_Time=df.Developer_Reply_Date_Time.fillna("9999-01-01T00:00:00Z")
    df.Developer_Reply_Date_Time=pd.to_datetime(df.Developer_Reply_Date_Time,dayfirst = True,errors='ignore')
    

    df=df.fillna('')

    for index,row in df.iterrows():
        warnings.filterwarnings("ignore")
        cur_row=row['Review_Text'].replace('.',' ').replace(',',' ').translate(str.maketrans('','',string.punctuation)).lower()
                    
        if len(cur_row)<2:
            df.set_value(index,'review_category','No_Reviews')
        elif cur_row.lower() in {"good", "very good", "nice", "awesome","ok"}:
            df.set_value(index,'review_category','Positive_Reviews')
        elif cur_row.lower() in {"bad", "very bad", "poor", "not good"} :
            df.set_value(index,'review_category','Miscellaneous')
        else:
            df.set_value(index,'review_category',classifier.classify(cur_row)[0]) 
                                  
    df=df.fillna('')

    df_records=df.to_dict(orient='records')

    try:
       es = Elasticsearch(config.es_address)
       timestamp = datetime.now().replace(microsecond = 0)
       for record in df_records:
           record['_index']=config.es_index_name
           record['_type']=config.es_type_name
           record['timestamp']=timestamp
      #record['Review_submit_month_year']=str(record['Review_Submit_Date_Time'].strftime("%b"))+'-'+str(record['Review_Submit_Date_Time'].year)
#           record['_id'] = (str(str(record['index'])+'_'+str(int((record['Transaction_dt'] - datetime(1970, 1, 1)).total_seconds()))) +'_'+str(record['Star_Rating'])+'_')	
           record['_id'] = (datetime.strftime(parse_date(str(record['Review_Submit_Date_Time'])).replace(tzinfo=None), formatStr) +'_'+ record['Device']+'_'+str(record['Star_Rating'])+'_'+record['review_category'])   
           #es.indices.delete(config.es_index_name,ignore=[400, 404])
       helpers.bulk(es,df_records)
    except Exception as ex:
        logger.error(ex)
#        sys.exit()     
