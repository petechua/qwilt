import requests
import getpass
import base64
import json

# Objective: Basic API tests for QC Services API - version 1.7.2
# Author: petec@qwilt.com
# Version: 1.0

# Configurations #
url_login="https://login.cqloud.com/login"
url_deployment="https://network-status.cqloud.com/api/4/network-status/deployment"
url_service="https://network-status.cqloud.com/api/4/network-status/service"
url_delivery_service="https://network-status.cqloud.com//api/4/network-status/delivery-service"
url_client_mapping="https://client-mapping.cqloud.com/api/1/cache-group"
url_log_reporting="https://reporting.cqloud.com/mdls"
url_qn_local_status="https://{QN_Delivery_IP}/static-content/status.json"
### Static inputs ###
#username="@qwilt.com"
#password="yourqcpassword"
#qnIds=""
#client_ip="x.x.x.x"
#qn_delivery_ip="x.x.x.x"

def get_api_response(api_desc,api_url,cq_login_token,params):
	headers= {'Cookie': 'cqloudLoginToken='+cq_login_token}
	#params = {'qnIds':qnid}
	r = requests.get(api_url, headers=headers, params=params)
	data = r.json()
	print("\n" + api_desc)
	print("#"*20)
	print(json.dumps(data, indent=4, sort_keys=True))
def get_mdls_response(api_desc,api_url,cq_login_token,params1,params2):
	headers = {'Cookie': 'cqloudLoginToken='+cq_login_token}
	joined_params = {}
	joined_params.update(params1)
	joined_params.update(params2)
	print(joined_params)
	### Preview prepared URL request with concatenate params
	#prereq = requests.Request('GET',api_url,params=joined_params)
	#prepared = prereq.prepare()
	#print(prepared.url)
	r = requests.get(api_url, headers=headers, params=joined_params)
	data = r.json()
	print("\n" + api_desc)
	print("#"*30)
	print(json.dumps(data, indent=4, sort_keys=True))
def get_qn_local_status(api_desc,api_url,cq_login_token,qn_ip):
	headers = {'Cookie': 'cqloudLoginToken='+cq_login_token}
	url_qn=api_url.replace("{QN_Delivery_IP}",qn_ip)
	#print(url_qn)
	r = requests.get(url_qn,headers=headers,verify=False)
	data = r.json()
	print("\n" + api_desc)
	print("#"*30)
	print(json.dumps(data, indent=4, sort_keys=True))

### Get User inputs ###
username = raw_input("Enter username: ")
password = getpass.getpass(prompt="Enter password: ")
qnIds = raw_input("Enter qnID: ")
client_ip = raw_input("Enter Client IP: ")
qn_delivery_ip = raw_input("Enter QN Delivery IP: ")

### Request Parameters ###
qnid_params = {'qnIds':qnIds}
client_ip_params = {'client-ip':client_ip}
cdn_params = {'cdn':"isp-cp"}
pagesize_params = {'pageSize':10}

response_login=requests.get(url_login, auth=(username,password),allow_redirects=False)

#print(response_login)
#print(response_login.status_code)
#print(response_login.cookies.get("cqloudLoginToken"))

get_api_response("Deployment API",url_deployment,response_login.cookies.get("cqloudLoginToken"),qnid_params)
get_api_response("Service API",url_service,response_login.cookies.get("cqloudLoginToken"),qnid_params)
get_api_response("Delivery Service API",url_delivery_service,response_login.cookies.get("cqloudLoginToken"),qnid_params)
get_api_response("Client Mapping API",url_client_mapping,response_login.cookies.get("cqloudLoginToken"),client_ip_params)
get_mdls_response("MDLs Download path listing",url_log_reporting,response_login.cookies.get("cqloudLoginToken"),cdn_params,pagesize_params)
#get_qn_local_status("QN Local status",url_qn_local_status,response_login.cookies.get("cqloudLoginToken"),qn_delivery_ip)