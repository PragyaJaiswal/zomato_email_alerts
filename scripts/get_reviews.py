#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import *

import requests
import pprint

def get_review():
	r = requests.get(
			'https://developers.zomato.com/api/v2.1/reviews?res_id={0}'.format(RES_ID),
			headers = {
				'user_key': API_KEY,
				'Accept': 'application/json'
				}
			)

	pprint.pprint(r.json()['user_reviews'])

if __name__ == '__main__':
	get_review()