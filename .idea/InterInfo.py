#!/usr/bin/env python
__author__ = 'Xic'

from urllib import request
import re

url = 'http://www.inter.it'

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User_Agent': user_agent}

# req = request.Request(url, headers)
data = request.urlopen(url)
html = data.read().decode('utf8')

print(html)