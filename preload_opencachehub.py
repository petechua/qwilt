#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
import requests
from tqdm import tqdm
from datetime import datetime

### Preload OpenCacheHub HLS video###
# Useful for Qwilt Open Trial
# Works by pre-fetching test URLs via OCN
# Utilise external Python library - requests & tqdm  i.e pip install requests
# Author: petec@qwilt.com - May 2020

### Configuration Parameters ###
# Sample QN URL - http://qn-01038-comnet-poc-1.opencachehub.qwilted-cds.cqloud.com/soccer_barcelona_atletico_madrid_abr/480_2M/index0.ts
OCH_protocol="http://"
QN_hostname="qn-01038-comnet-poc-1.opencachehub.qwilted-cds.cqloud.com"
OCH_baseurl="/soccer_barcelona_atletico_madrid_abr/"
OCH_resolution=["480_1M","480_2M","720_3M","720_4M","1080_5M","1080_8M","2160_20M","2160_35M"]
OCH_numchunks=5 #Number of .ts chunks in each resolution
num_preflights_items=1 + (len(OCH_resolution))*2 # Master playlist + variant playlists + 0.ts of each variant
num_preflight_checks=0
now = datetime.now()
log_filename="log-" + now.strftime("%Y%m%d_%H%M%S") + ".txt"
f = open(log_filename,"w+")

################################

#user_hls_url=raw_input()
#print(preflight_manifest(user_hls_url))

master_playlist_url=OCH_protocol+QN_hostname+OCH_baseurl+"index.m3u8"
print(master_playlist_url)

print("The number of resolutions in stream are: %d" %len(OCH_resolution))
print("The number of preflight test-items are: %d" %num_preflights_items)
print("\n") 

def preflight_manifest(f_url):
	global num_preflight_checks
	now = datetime.now()
	preflight_manifest_response=requests.get(f_url)
	if preflight_manifest_response.status_code==200 and preflight_manifest_response.headers['content-type']=="application/vnd.apple.mpegurl":
		#print(preflight_manifest_response.text)
		num_preflight_checks += 1
		now = datetime.now()
		logentry=now.strftime("%D:%H:%M:%S") + " " + str(preflight_manifest_response.status_code) + " " + preflight_manifest_response.headers['X-OC-Service-Type'] + " " + preflight_manifest_response.headers['content-type'] + " " + f_url + "\n"
		f.write(logentry)
		return "true"

def preflight_chunk(c_url):
	global num_preflight_checks
	now = datetime.now()
	preflight_chunk_response=requests.get(c_url)
	if preflight_chunk_response.status_code==200 and preflight_chunk_response.headers['content-type']=="video/mp2t":
		num_preflight_checks += 1
		logentry=now.strftime("%D:%H:%M:%S") + " " + str(preflight_chunk_response.status_code) + " " + preflight_chunk_response.headers['X-OC-Service-Type'] + " " + preflight_chunk_response.headers['content-type'] + " " + c_url + "\n"
		f.write(logentry)
		return "true"

def preflight_test():
	global num_preflight_checks
	# Preflight for master playlist
	print("Starting preflight checks...")
	test_master_playlist=preflight_manifest(master_playlist_url)
	if test_master_playlist=="true":
		print("Master playlist passed preflight test...")
		#num_preflight_checks += 1
	else:
		print("Master playlist failed preflight test...")
	# Preflight for variant playlist % chunks
	for i in tqdm(OCH_resolution):
		variant_playlist_url=OCH_protocol+QN_hostname+OCH_baseurl+i+"/index.m3u8"
		preflight_manifest(variant_playlist_url)
		for j in range(OCH_numchunks):
			if j==0:
				#print("This is chunk:",j)
				chunk_url=OCH_protocol+QN_hostname+OCH_baseurl+i+"/index"+str(j)+".ts"
				preflight_chunk(chunk_url)
		print(i + " chunks fetching completed.")
	print("The number of successful preflight checks are: %s" %num_preflight_checks)
	print("The logfile is: %s" %log_filename)

def preload():
	for i in tqdm(OCH_resolution):
		for j in range(OCH_numchunks):
				chunk_url=OCH_protocol+QN_hostname+OCH_baseurl+i+"/index"+str(j)+".ts"
				preflight_chunk(chunk_url)
		print(i + " chunks fetching completed.")


### Preflight tests ###
# Preflight test will attempt to fetch master playlist, variant playlists and 0.ts for each variant. 
# To pass preflight, all requests must return response code of 200 and corresponding content-type

preflight_test()
if num_preflight_checks == num_preflight_checks:
	print("\nAll preflight tests are successful.")
	print("Starting preload...")
	preload()

else:
	print("Prefetching conditions not met, prefetching terminated...")
f.close()
#print(QN_hostname)
#print(OCH_baseurl)
#for i in OCH_resolution:
#	for j in range(OCH_numchunks):
#		if j==0:
#			print("This is chunk:",j)
#		chunk_url=OCH_protocol+QN_hostname+OCH_baseurl+i+"/index"+str(j)+".ts"
#		print(chunk_url)
#		now = datetime.now()
#		r=requests.get(chunk_url)
		#print(now.strftime("%D:%H:%M:%S"),r.status_code,r.headers['X-OC-Service-Type'],r.headers['content-type'])
#		logentry=now.strftime("%D:%H:%M:%S") + " " + str(r.status_code) + " " + r.headers['X-OC-Service-Type'] + " " + r.headers['content-type'] + " " + chunk_url + "\n"
#		f.write(logentry)
#	print(i + " chunks fetching completed.")
#f.close()
#print("The number of successful preflight checks are: ",num_preflight_checks)
#for i in range(OCH_numchunks):
	#print(i)
