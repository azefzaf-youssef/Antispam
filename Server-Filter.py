import nltk
import smtpd
import asyncore
import smtplib
import traceback
import re
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from joblib import load
from sklearn.metrics import accuracy_score

class CustomSMTPServer(smtpd.SMTPServer):



    tfidf_vectorizer = TfidfVectorizer()
    nltk.download('stopwords')
    stemmer = SnowballStemmer('english')
    stop_words = stopwords.words('english')
    tfidf_vectorizer = load('tfidf_vectorizer.joblib')

    def preprocess_text(self , text , stop_words):
        text = re.sub(r'[\r\n]', ' ', text)
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = text.lower()
        tokens = [self.stemmer.stem(word) for word in text.split() if word not in self.stop_words]
        return ' '.join(tokens)

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        mailfrom = mailfrom.replace('\'', '')
        mailfrom = mailfrom.replace('\"', '')
        text=self.preprocess_text(data.decode('utf-8'),self.stop_words)
        X_test_new2 = self.tfidf_vectorizer.transform([text])
        model = load('Support_Vector_Machine_best_model.pkl')
        predictions = model.predict(X_test_new2)
        print(f'Accuracy: {predictions[0]}')

        for i in range(len(rcpttos)):
            rcpttos[i] = rcpttos[i].replace('\'', '')
            rcpttos[i] = rcpttos[i].replace('\"', '')

        try:
            # Convert header string to bytes and add custom header 'X-Spam: YES'
            if predictions[0] == 1 :
               header = b"X-Spam:YES\n"
               data = header+data
            else :
               header = b"X-Spam:No\n"
               data = header+data

            # DO WHAT YOU WANNA DO WITH THE EMAIL HERE
            # In the future, you can include more functions for user convenience,
            # such as functions to change fields within the body (From, Reply-to etc),
            # and/or to send error codes/mails back to Postfix.
            # Error handling is not really fantastic either.

            pass
        except Exception as e:
            print('Something went south:', e)
            print(traceback.format_exc())

        try:
            with smtplib.SMTP('localhost', 10026) as server:
                server.starttls()
                server.sendmail(mailfrom, rcpttos, data)
            #print('send successful')
        except (smtplib.SMTPException, smtplib.SMTPServerDisconnected, smtplib.SMTPResponseException,
                smtplib.SMTPSenderRefused, smtplib.SMTPRecipientsRefused, smtplib.SMTPDataError,
                smtplib.SMTPConnectError, smtplib.SMTPHeloError, smtplib.SMTPAuthenticationError) as e:
            print('Exception:', e)

        except Exception as e:
            print('Undefined exception:', e)
            print(traceback.format_exc())

server = CustomSMTPServer(('127.0.0.1', 10025),None)
asyncore.loop()


