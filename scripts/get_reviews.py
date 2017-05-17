#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import division
from config import *

import os, sys
import subprocess

import json
import time
import datetime

import hashlib

import requests

import sendgrid
from sendgrid.helpers.mail import *

from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

import MySQLdb as db


def get_review():
    restaurant_reviews = {}
    for res_id in ZOMATO_RES_IDS:
        MySQL().mysql_log('FETCH_REVIEWS', str(os.environ['LOGNAME']), 'Starting fetch for res_id {0}'.format(res_id))
        try:
            r = requests.get(
                    'https://developers.zomato.com/api/v2.1/reviews?res_id={0}'.format(res_id),
                    headers = {
                        'user_key': ZOMATO_API_KEY,
                        'Accept': 'application/json'
                        }
                    )
            for each in r.json()['user_reviews']:
                restaurant_reviews.setdefault(res_id, []).append(
                    (each['review']['review_text'], each['review']['rating'])
                    )
        except requests.ConnectionError as e:
            print 'Error', res_id
            if e:
                MySQL().mysql_log('FETCH_REVIEWS', str(os.environ['LOGNAME']), 'Fetch failed for {0}. Connection Error.'.format(res_id))
            else:
                MySQL().mysql_log('FETCH_REVIEWS', str(os.environ['LOGNAME']), 'Fetch failed for {0}.'.format(res_id))


    for res_id, all_reviews in restaurant_reviews.iteritems():
        MySQL().mysql_log('DUMP_REVIEWS', str(os.environ['LOGNAME']), 'Dumping reviews for {0}.'.format(res_id))
        for review in all_reviews:
            '''
            review[0] - Review
            review[1] - Rating
            '''
            try:
                MySQL().mysql_dump(res_id, review[0].encode('utf-8'), review[1])
            except Exception, e:
                MySQL().mysql_log('DUMP_REVIEWS', str(os.environ['LOGNAME']), 'Failed to dump reviews for {0}.'.format(res_id))


class MySQL(object):
    """docstring for MySQL"""
    def __init__(self):
        super(MySQL, self).__init__()

    def mysql_setup(self, table_name = 'REVIEWS', database_name = 'zomato_alerts'):
        cur.execute('CREATE DATABASE IF NOT EXISTS {0};'.format(database_name))
        cur.execute('use {0};'.format(database_name))
        if table_name == 'LOGS':
            cur.execute('''CREATE TABLE IF NOT EXISTS {0} (
                TIMESTAMP   CHAR(50)    NOT NULL,
                ACTION      CHAR(20)    NOT NULL,
                USER        CHAR(50)    NOT NULL,
                DB_USER     CHAR(20)    NOT NULL,
                META_DATA   TEXT        NOT NULL)'''.format(table_name))
        else:
            cur.execute('''CREATE TABLE IF NOT EXISTS {0} (
                REVIEW_HASH CHAR(50)        NOT NULL    PRIMARY KEY,
                RES_ID      CHAR(20)        NOT NULL,
                RES_REVIEWS LONGTEXT        NOT NULL,
                RES_RATING  CHAR(20)        NOT NULL,
                PROCESSED   BOOLEAN         NOT NULL,
                Class       CHAR(20)        NULL)'''.format(table_name))
        con.commit()


    def mysql_dump(self, res_id, review, rating, table_name = 'REVIEWS', database_name = 'zomato_alerts'):
        cur.execute('''INSERT INTO {0}(REVIEW_HASH, RES_ID, RES_REVIEWS, RES_RATING, PROCESSED) VALUES (%s, %s, %s, %s, %s)'''.format(table_name), (str(hashlib.md5(review.decode('utf-8')).hexdigest()), str(res_id), review, str(rating), 0))
        con.commit()


    def mysql_log(self, action, user, message, table_name = 'LOGS', database_name = 'zomato_alerts'):
        cur.execute('use {0};'.format(database_name))
        cur.execute('''INSERT INTO {0}(TIMESTAMP, ACTION, USER, DB_USER, META_DATA) VALUES (%s, %s, %s, %s, %s)'''.format(table_name),
            (
                datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                action, user, DB_USER, message)
            )
        con.commit()


    def mysql_query(self, table_name = 'REVIEWS', database_name = 'zomato_alerts'):
        count = 0
        neg_count = 0
        neg_reviews = []
        
        cur.execute('''SELECT * FROM {0} WHERE Processed = 0'''.format(table_name))
        data = cur.fetchall()
        total_reviews_processed = len(data)
        
        if total_reviews_processed == 0:
            MySQL().mysql_log('PROCESS_REVIEWS', str(os.environ['LOGNAME']), 'No unprocessed reviews.')
        else:
            MySQL().mysql_log('PROCESS_REVIEWS', str(os.environ['LOGNAME']), 'Processing reviews.')
            for row in data:
                count += 1
                MySQL().mysql_log('PROCESS_REVIEWS', str(os.environ['LOGNAME']), 'Processed {0} of {1} unprocessed reviews.'.format(count, total_reviews_processed))
                print 'Processed {0} of {1} unprocessed reviews.'.format(count, total_reviews_processed)
                '''
                row[0] - review_hash
                row[1] - res_id
                row[2] - review
                row[3] - rating
                row[4] - processed status
                '''
                sentiment_class = sentiment_analysis(row[2], row[3])
                MySQL().mysql_log('PROCESS_REVIEWS', str(os.environ['LOGNAME']), "Sentiment Calculated. Updating reviews' process status.")
                if sentiment_class.classification == 'neg' and float(row[3]) <= float(3):
                    neg_count+=1
                    neg_reviews.append(row[2])
                    cur.execute('''UPDATE {0} SET Processed = %s, Class = %s WHERE REVIEW_HASH = %s'''.format(table_name), (1, 'neg', str(row[0])))
                else:
                    cur.execute('''UPDATE {0} SET Processed = %s, Class = %s WHERE REVIEW_HASH = %s'''.format(table_name), (1, 'pos', str(row[0])))
                con.commit()
            
            if neg_count > 0:
                MySQL().mysql_log('GENERATE ALERT', str(os.environ['LOGNAME']), 'Creating subject and body of email.')
                subject = 'Percentage of negative reviews: {0}'.format((neg_count/total_reviews_processed)*100)
                body = 'Number of reviews processed: {0}\nNumber of negative reviews: {1}\nSome negative reviews: {2}'.format(total_reviews_processed, neg_count, str(neg_reviews[:3]))
                # print subject, body
                send_email(subject, body)
            else:
                MySQL().mysql_log('ALERT NOT NEEDED', str(os.environ['LOGNAME']), 'Yay! No negative reviews found among new reviews.')


def sentiment_analysis(review, rating):
    sentiment_class = TextBlob(
                            str(review.decode('utf-8')),
                            analyzer = NaiveBayesAnalyzer()
                            ).sentiment
    return sentiment_class


def send_email(subject, body):
    MySQL().mysql_log('SEND ALERT', str(os.environ['LOGNAME']), "Negative reviews found. Preparing alert.")
    try:
        sg = sendgrid.SendGridAPIClient(apikey = SENDGRID_API_KEY)
        
        from_email = Email(FROM_EMAIL)
        to_email = Email(TO_EMAIL)
        content = Content("text/plain", str(body))

        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        MySQL().mysql_log('SEND ALERT', str(os.environ['LOGNAME']), "Email alert sent.")
    except Exception, e:
        MySQL().mysql_log('SEND ALERT', str(os.environ['LOGNAME']), "Alert failed to be sent. Exception handled. {0}". format(e))


def setup_configuration(command):
    subprocess.check_call(command, shell = True)


if __name__ == '__main__':
    if sys.platform.startswith('linux'):
        # for command in SHELL_COMMANDS:
        #     setup_configuration(command)

        '''Connect to database'''
        con = db.connect(user=DB_USER, passwd=DB_PASSWORD)
        cur = con.cursor()
        MySQL().mysql_setup('LOGS')
        MySQL().mysql_setup('REVIEWS')

        get_review()
        MySQL().mysql_query()
        con.close()
    else:
        print 'To be implemented'