#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv, json, re

import requests

import time
import datetime
import pprint

import sendgrid
from sendgrid.helpers.mail import *

from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

import MySQLdb as db

# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize, RegexpTokenizer
# from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
# from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

from config import *

def get_review():
    restaurant_reviews = {}
    for res_id in ZOMATO_RES_IDS:
        mysql_logging('FETCH_REVIEWS', str(os.environ['USER']), 'Starting fetch for res_id {0}'.format(res_id))
        try:
            r = requests.get(
                    'https://developers.zomato.com/api/v2.1/reviews?res_id={0}'.format(res_id),
                    headers = {
                        'user_key': ZOMATO_API_KEY,
                        'Accept': 'application/json'
                        }
                    )
        except requests.ConnectionError as e:
            if e:
                mysql_logging('FETCH_REVIEWS', str(os.environ['USER']), 'Fetch failed for {0}. Connection Error.'.format(res_id))
            else:
                mysql_logging('FETCH_REVIEWS', str(os.environ['USER']), 'Fetch failed for {0}.'.format(res_id))
        
        # pprint.pprint(r.json()['user_reviews'])
        # raw_input()
        for each in r.json()['user_reviews']:
            restaurant_reviews.setdefault(res_id, []).append(
                (each['review']['review_text'], each['review']['rating'])
                )

    # print pprint.pprint(restaurant_reviews)
    for res_id, all_reviews in restaurant_reviews.iteritems():
        mysql_logging('DUMP_REVIEWS', str(os.environ['USER']), 'Dumping reviews for {0}.'.format(res_id))
        for review in all_reviews:
            # print review[0], review[1]
            # mysql_logging('LOGS', res_id, review[0], review[1])
            try:
                mysql_dump(res_id, review[0].encode('utf-8'), review[1])
            except Exception, e:
                mysql_logging('DUMP_REVIEWS', str(os.environ['USER']), 'Failed to dump reviews for {0}.'.format(res_id))

    
    for res_id, reviews in restaurant_reviews.iteritems():
        for each in reviews:
            # print each[0], each[1]
            # print TextBlob(each[0]).sentiment      
            
            '''
            # returns Polarity at index 0 and subjectvity at index 1
            # Polarity:     negative vs positive    (-1.0 -> 1.0)
            # Subjectivity: objective vs subjective (0.0 -> 1.0)
            # Intensity:    modifies next word?     (x0.5 -> x2.0)
            '''
            
            sentiment_class = TextBlob(
                                    each[0],
                                    analyzer = NaiveBayesAnalyzer()
                                    ).sentiment
            if sentiment_class.classification == 'neg' and int(each[1]) <= 3:
                print each[0], sentiment_class.classification, int(each[1])
            raw_input()
    


def mysql_setup(table_name = 'REVIEWS', database_name = 'zomato_alerts'):
    cur.execute('CREATE DATABASE IF NOT EXISTS {0};'.format(database_name))
    cur.execute('use {0};'.format(database_name))
    if table_name == 'LOGS':
        cur.execute('''CREATE TABLE IF NOT EXISTS {0} (
            TIMESTAMP   CHAR(50)    NOT NULL,
            ACTION      CHAR(20)    NOT NULL,
            USER        TEXT        NOT NULL,
            DB_USER     CHAR(20)    NOT NULL,
            META_DATA   CHAR(50)    NOT NULL)'''.format(table_name))
    else:
        cur.execute('''CREATE TABLE IF NOT EXISTS {0} (
            RES_ID      CHAR(20)        NOT NULL,
            RES_REVIEWS LONGTEXT        NOT NULL,
            RES_RATING  CHAR(20)        NOT NULL,
            PROCESSED   BOOLEAN         NOT NULL)'''.format(table_name))


def mysql_dump(res_id, review, rating, table_name = 'REVIEWS', database_name = 'zomato_alerts'):
    cur.execute('''INSERT INTO {0}(RES_ID, RES_REVIEWS, RES_RATING, PROCESSED) VALUES (%s, %s, %s, %s)'''.format(table_name), (str(res_id), review, str(rating), 0))

    con.commit()


def mysql_logging(action, user, message, table_name = 'LOGS', database_name = 'zomato_alerts'):
    cur.execute('use {0}'.format(database_name))
    cur.execute('''INSERT INTO {0}(TIMESTAMP, ACTION, USER, DB_USER, META_DATA) VALUES (%s, %s, %s, %s, %s)'''.format(table_name),
        (
            datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
            action, user, DB_USER, message)
        )
    con.commit()


def send_email():
    sg = sendgrid.SendGridAPIClient(apikey = SENDGRID_API_KEY)
    from_email = Email("pragya.jswl@gmail.com")
    subject = "TRYYYYYY! :p"
    to_email = Email("pragya.jswl@gmail.com")
    content = Content("text/plain", "Pliss, work. Pliss!")
    
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    
    # print(response.status_code)
    # print(response.body)
    # print(response.headers)


if __name__ == '__main__':
    '''Connect to database'''
    con = db.connect(user=DB_USER, passwd=DB_PASSWORD)
    cur = con.cursor()
    mysql_setup('LOGS')
    mysql_setup('REVIEWS')
    # mydb = pw.MySQLDatabase('test', user=DB_USER, passwd=DB_PASSWORD)

    get_review()
    # send_email()
    # # nltk.download('stopwords')
    # stop = [word for word in stopwords.words('english') if not word == 'not']
    # # stop = set(stopwords.words('english')) - set('not')

    # with open('../data/yelp_labelled.tsv') as infile:
    #   data = csv.reader(infile, dialect = 'excel-tab')
    #   sentiment_analysis(data, stop)