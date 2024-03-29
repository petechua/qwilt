#!/usr/local/bin/python3
import requests
import m3u8
from datetime import datetime
import re
from tqdm import tqdm
import sys
import ssl

### Preload generic HLS video###
# Useful for HLS ABR stream
# Works by pre-fetching all the .ts chunks in variant playlists. Works for single variant and multiple-variants playlist.
# Utilise various external Python library - requests & tqdm & m3u8 i.e pip install requests
# Author: petec@qwilt.com - June 2020
# Version: 1.10

### Configurations ###
# Sample master playlist - http://qn-01038-comnet-poc-1.opencachehub.qwilted-cds.cqloud.com/soccer_barcelona_atletico_madrid_abr/index.m3u8
# Sample variant playlist - http://qn-01038-comnet-poc-1.opencachehub.qwilted-cds.cqloud.com/soccer_barcelona_atletico_madrid_abr/480_2M/index.m3u8

segments_list = []
resolution_list = []
num_preflight_success=0
num_200_segment = 0
num_local_segment = 0
num_relay_segment = 0
now = datetime.now()
log_filename="log-" + now.strftime("%Y%m%d_%H%M%S") + ".txt"
on_screen_log="false" # Display log output on screen during request?
f = open(log_filename,"w+")
baseurl=""

## Functions ##

def check_playlist(input_url):
	#print("Entering checklist")
	#print(input_url)
	preflight_playlist_response=requests.head(input_url)
	#print(preflight_playlist_response.status_code)
	#print(preflight_playlist_response.headers['content-type'])
	#if preflight_playlist_response.status_code==200 and (preflight_playlist_response.headers['content-type']=="application/vnd.apple.mpegurl"):
	if preflight_playlist_response.status_code==200:
		return "true"
	else:
		return "false"

def get_baseurl():
	m = re.search('(.+?)index\.m3u8',user_hls_playlist)
	global baseurl
	if m:
		baseurl = m.group(1)
		#print("Printing from getbaseurl functions: ", baseurl)

# Get the range of segments in a playlist
def get_segments(input_url):
	hls_playlist=m3u8.load(input_url)
	for segments in hls_playlist.segments:
		#print(segments)
		#n = re.findall("(.+?)\.ts",str(segments))
		n = re.findall("\d+.ts",str(segments))
		if n:
			segments_list.append(n)
	#print("here is def get_segments")
	#print(segments_list)

# Fetch a segment
def fetch_segments(input_url):
	now = datetime.now()
	global num_200_segment
	global num_local_segment
	global num_relay_segment
	segment_response=requests.get(input_url)
	#if segment_response.status_code==200 and segment_response.headers['content-type']=="video/mp2t":
	if segment_response.status_code==200:
		try:
			logentry=now.strftime("%D:%H:%M:%S") + " " + str(segment_response.status_code) + " " + segment_response.headers['X-OC-Service-Type'] + " " + segment_response.headers['content-type'] + " " + input_url + "\n"
			if segment_response.headers['X-OC-Service-Type'] == "lo":
				num_local_segment += 1
			if segment_response.headers['X-OC-Service-Type'] == "re":
				num_relay_segment += 1
		except KeyError:
			logentry=now.strftime("%D:%H:%M:%S") + " " + str(segment_response.status_code) + " " + "origin" + " " + segment_response.headers['content-type'] + " " + input_url + "\n"
		f.write(logentry)
		if segment_response.status_code == 200:
			num_200_segment += 1
		if (on_screen_log=="true"):
			print(logentry)
		return "true"

def check_preflight(playlist_type,flight_type):
	global num_preflight_success
	logentry="Start of "+flight_type+"\n#########################\n"
	f.write(logentry)		
	if(playlist_type):
		print(flight_type+" in ABR playlist...")
		print("Number of required successful preflight items: " + str(num_preflight_condition))
		# Preflight for playlists
		#Delete - for variant in resolution_list:
		for variant in hls_playlist.playlists:
			#print(" ".join(map(str,variant)))
			#temp_playlist=baseurl+" ".join(map(str,variant))+"/index.m3u8"
			#temp_playlist=baseurl+" ".join(map(str,variant))+".m3u8"
			temp_playlist=baseurl+str(variant.uri)
			#print(temp_playlist)
			if(check_playlist(temp_playlist)) == "true":
				num_preflight_success += 1
		
		# Preflight for segments
		for variant in tqdm(resolution_list):
			print("Fetching "+str(variant)+"...")
			for segments in range(len(segments_list)):
				if flight_type=="preflight":
					if segments == 0:
						#temp_segment=baseurl+" ".join(map(str,variant))+ "/" +" ".join(map(str,segments_list[segments])) + ".ts"
						#temp_segment=baseurl+" ".join(map(str,segments_list[segments])) + ".ts"
						temp_segment=baseurl+" ".join(map(str,variant))+ "/" +" ".join(map(str,segments_list[segments]))
						#print(baseurl)
						#print(variant)
						#print(segments_list[segments])
						#print(temp_segment)
						if (fetch_segments(temp_segment)) == "true":
							num_preflight_success += 1
				else:
					#temp_segment=baseurl+" ".join(map(str,variant))+ "/" +" ".join(map(str,segments_list[segments])) + ".ts"
					#temp_segment=baseurl+" ".join(map(str,segments_list[segments])) + ".ts"
					temp_segment=baseurl+" ".join(map(str,variant))+ "/" +" ".join(map(str,segments_list[segments]))
					#print(baseurl)
					#print(temp_segment)
					if (fetch_segments(temp_segment)) == "true":
						num_preflight_success += 1

	else:
		print(flight_type+" in single variant playlist...")
		if flight_type == "preflight":
			print("Number of required successful preflight items: " + str(num_preflight_condition))
			if(check_playlist(user_hls_playlist)) == "true":
					num_preflight_success += 1
			temp_segment = baseurl +" ".join(map(str,segments_list[0])) + ".ts"
			#print(temp_segment)
			if (fetch_segments(temp_segment)) == "true":
				num_preflight_success += 1
		else:
			for segments in tqdm(range(len(segments_list))):
				temp_segment=baseurl+" ".join(map(str,segments_list[segments])) + ".ts"
				#print(temp_segment)
				if (fetch_segments(temp_segment)) == "true":
					num_preflight_success += 1
	logentry="#########################\nEnd of "+flight_type+"\n"
	f.write(logentry)	

#print("Enter URL of playlist:")
#user_hls_playlist=input("Enter URL of playlist: ")

#user_hls_playlist='http://qn-01038-comnet-poc-1.opencachehub.qwilted-cds.cqloud.com/soccer_barcelona_atletico_madrid_abr/480_2M/index.m3u8'
#user_hls_playlist='http://origin.videos.opencachehub.com/video06/index.m3u8'
#user_hls_playlist='http://172.16.1.72:9000/hls/index.m3u8'
user_hls_playlist='http://172.16.1.72:10000/hls/index.m3u8'
#user_hls_playlist='http://172.16.1.72:10000/hls/clpr_126976_clipper_LBR.m3u8'

# Validate input URL as m3u8 playlist & retreive ABR resolutions
if check_playlist(user_hls_playlist) == "true":
	print("Input playlist is valid: " + user_hls_playlist)
	hls_playlist=m3u8.load(user_hls_playlist)
	
	### Condition to pass preflight checks
	print("\nPreflight Test Conditions")
	print("#"*100)
	print("Preflight test will attempt to fetch master playlist, variant playlists and 0.ts for each variant playlist.\nTo pass preflight, all requests must return response code of 200 and correct corresponding content-type")
	print("#"*100)
	if hls_playlist.is_variant:
		print("\nThis is ABR playlist...")
		get_baseurl()
		temp_variant_playlist=baseurl+hls_playlist.playlists[0].uri
		#print("Before entering get segments, variant url is:")
		#print(temp_variant_playlist)
		get_segments(temp_variant_playlist)
		
		# Find all resolutions in the master playlist
		for playlist in hls_playlist.playlists:
			#print(playlist.uri)
			#r = re.findall("(.+?)/index\.m3u8",playlist.uri)
			r = re.findall("(.+?)/*\.m3u8",playlist.uri)
			if r:
				#print(r)
				resolution_list.append(r)
				#print(playlist.stream_info.bandwidth)
		print("The len of resolution_list list is...",len(resolution_list))
		num_preflight_condition=len(resolution_list)*2
		check_preflight(hls_playlist.is_variant,"preflight")
		print("The number of variant playlists is: "+str(len(resolution_list))+" and number of segments per playlist is: "+str(len(segments_list)))
		print("The number of successful preflight items completed: "+str(num_preflight_success))
	else:
		get_baseurl()
		get_segments(user_hls_playlist)
		num_preflight_condition=2 #<-------- hmmmmmm
		print("\nThis is likely a single variant playlist...")
		print("The number of variant playlist is: 1 and number of segments per playlist is: "+str(len(segments_list)))
		check_preflight(hls_playlist.is_variant,"preflight")
		print("The number of successful preflight items completed: "+str(num_preflight_success))
else:
	print("Input playlist is invalid: "+user_hls_playlist+"\nExiting...")
	sys.exit()

if num_preflight_success == num_preflight_condition:
	print("\nAll preflight conditions met, prefetch may continue...")
	choice_fetch = input("Press (C) to continue with prefetch and (Q) to Quit: ")
	if choice_fetch == "C" or choice_fetch == "c":
		print("C is selected")
		### Continue with prefetching
		check_preflight(hls_playlist.is_variant,"fetching")
		print("\nThe number of transactions with 200 Response code is: "+str(num_200_segment))
		print("\nThe number of segments delivered via relay is: "+str(num_relay_segment))
		print("\nThe number of segments delivered via local is: "+str(num_local_segment))
	elif choice_fetch == "Q" or choice_fetch == "q":
		print("Q is selected")
	else:
		print("Not valid input...")
else:
	print("Preflight conditions not met, terminating...")
	sys.exit()

f.close()
print("\nAll transactions are logged in: "+log_filename)
print("End of program")
