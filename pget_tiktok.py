#!/usr/local/bin/python3
import requests
from datetime import datetime
import re
from tqdm import tqdm
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

### pget for downloading web objects ###
# Useful for downloading web objects that needs specific HTTP request headers
# Author: iampetechua@gmail.com
# Version: 1.0

## Configurations ##
website = "toktok.com"
header_Referer = {'Referer: https://www.tiktok.com/'}
header_UA = {'user-agent': 'my-app/0.0.1'}

## User inputs ##
web_obj_url = input("Enter Tiktok web-object URL: ")
web_obj_filename = input("Enter desired web-object filename: ")

### Functions ##
def dl_web_obj(web_obj_url,web_obj_filename):
	print("Entering this function...")
	print(web_obj_url, web_obj_filename)
	#web_obj_response=requests.head(web_obj_url,verify=False)
	web_obj_response=requests.get(web_obj_url, headers=header_Referer, verify=False)
	open(web_obj_filename,'wb').write(web_obj_response.content)
	print(web_obj_response.status_code)

## Main body of code ##
dl_web_obj(web_obj_url,web_obj_filename)