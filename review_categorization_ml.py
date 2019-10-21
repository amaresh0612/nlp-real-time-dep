import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, chi2
from text_cleaning import clean_corpus

class ReviewClassifier(object):
        
    def __init__(self,tfidf,selectKBest,dataframe,model):
        self.tfidf=tfidf
        self.selectKBest=selectKBest
        self.df=dataframe
        self.model=model
       
    def extract_featuresAndLabels(self):
        
        self.df=self.df[pd.notnull(self.df['Review Text'])]
        col = ['Category', 'Review Text']        
        self.df = self.df[col]      
        self.df.columns=['Category','Review_Text']     
        self.df['Review_Text'] = clean_corpus(self.df['Review_Text'])
        self.df['Category_id']=self.df['Category'].factorize()[0]                
        category_id_df=self.df[['Category','Category_id']].drop_duplicates().sort_values('Category_id')
        
        #category_to_id=dict(category_id_df.values)        
        self.id_to_category = dict(category_id_df[['Category_id', 'Category']].values)
        
        self.features = self.tfidf.fit_transform(self.df.Review_Text).toarray()        
        self.labels= self.df.Category_id

    def train_model(self):      
        X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(self.features, self.labels, self.df.index, test_size=0.10, random_state=0) 
        self.model.fit(self.features, self.labels)

    def classify(self,text):
        texts=[]
        texts.append(text)
        text_features = self.tfidf.transform(texts)
        predictions = self.model.predict(text_features)
        review_predicted=[]
        for text, predicted in zip(texts, predictions):
            review_predicted.append(self.id_to_category[predicted])
        return review_predicted
