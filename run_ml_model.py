from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
#from sklearn.svm import LinearSVC
import pandas as pd
from review_categorization_ml_indo import ReviewClassifier
#import pickle as pkl
import config_indo as config
import traceback
from sklearn.externals import joblib
from sklearn.neighbors import KNeighborsClassifier
#from sklearn.multiclass import OneVsRestClassifier
#from sklearn.naive_bayes import MultinomialNB
#### store classifier object to a file - persist the object ####

try:
        tfidf=TfidfVectorizer(sublinear_tf=True, min_df=2,max_df=0.9, norm='l2', encoding='latin-1', ngram_range=(1, 2),stop_words=("english","indonesian"))
#        model=LinearSVC(C=0.5, penalty= 'l1', max_iter =3000, dual=False)
        selectKBest=SelectKBest(chi2, k=500)
        model =KNeighborsClassifier(n_neighbors=5, algorithm='brute', metric='cosine')
#        model =OneVsRestClassifier(MultinomialNB())
        dataframe = pd.DataFrame()
        dataframe=pd.read_csv(config.ml_training_data_file,encoding = "ISO-8859-1")
        classifier=ReviewClassifier(tfidf,selectKBest,dataframe,model)
        #### extract features and lables #####
        classifier.extract_featuresAndLabels()
        #### train model #####
        classifier.train_model()        
        joblib.dump(classifier,open(config.object_ser_classifier_file,'wb'))
        
        print("review classifier has been created and persisted to file system successfully")  

except:
        print(str(traceback.format_exc()))
