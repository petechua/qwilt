#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
import requests
import m3u8
from datetime import datetime
import re
from tqdm import tqdm
import sys

### Preload generic HLS video###
# Useful for HLS ABR stream
# Works by pre-fetching all the .ts chunks in variant playlists. Works for single variant and multiple-variants playlist.
# Utilise various external Python library - requests & tqdm & m3u8 i.e pip install requests
# Author: petec@qwilt.com - June 2020
# Version: 1.00

### Configurations ###
# Sample master playlist - http://qn-01038-comnet-poc-1.opencachehub.qwilted-cds.cqloud.com/soccer_barcelona_atletico_madrid_abr/index.m3u8
# Sample variant playlist - http://qn-01038-comnet-poc-1.opencachehub.qwilted-cds.cqloud.com/soccer_barcelona_atletico_madrid_abr/480_2M/index.m3u8

segments_list = []
resolution_list = []
num_preflight_success=0
now = datetime.now()
log_filename="log-" + now.strftime("%Y%m%d_%H%M%S") + ".txt"
f = open(log_filename,"w+")

## Functions ##

def check_playlist(input_url):
	print(input_url)
	preflight_playlist_response=requests.head(input_url)
	if preflight_playlist_response.status_code==200 and preflight_playlist_response.headers['content-type']=="application/vnd.apple.mpegurl":
		return "true"
	else:
		return "false"

def get_baseurl():
	m = re.search('(.+?)index\.m3u8',user_hls_playlist)
	global baseurl
	if m:
		baseurl = m.group(1)
		print("Printing from getbaseurl functions: ", baseurl)

# Get the range of segments in a playlist
def get_segments(input_url):
	hls_playlist=m3u8.load(input_url)
	for segments in hls_playlist.segments:
		n = re.findall("(.+?)\.ts",str(segments))
		if n:
			segments_list.append(n)
	print("here is def get_segments")
	print(segments_list)

# Fetch a segment
def fetch_segments(input_url):
	now = datetime.now()
	segment_response=requests.get(input_url)
	if segment_response.status_code==200 and segment_response.headers['content-type']=="video/mp2t":
		logentry=now.strftime("%D:%H:%M:%S") + " " + str(segment_response.status_code) + " " + segment_response.headers['X-OC-Service-Type'] + " " + segment_response.headers['content-type'] + " " + input_url + "\n"
		f.write(logentry)
		return "true"

def check_preflight(playlist_type):
	global num_preflight_success
	logentry="Start of Preflight Check\n#########################\n"
	f.write(logentry)		
	if(playlist_type):
		print("Preflight in ABR playlist...")
		print("Number of required successful preflight items: " + str(num_preflight_condition))
		# Preflight for playlists
		for variant in resolution_list:
			#print(" ".join(map(str,variant)))
			temp_playlist=baseurl+" ".join(map(str,variant))+"/index.m3u8"
			#print(temp_playlist)
			if(check_playlist(temp_playlist)) == "true":
				num_preflight_success += 1
		# Preflight for segments
		for variant in tqdm(resolution_list):
			for segments in range(len(segments_list)):
				if segments == 0:
					temp_segment=baseurl+" ".join(map(str,variant))+ "/" +" ".join(map(str,segments_list[segments])) + ".ts"
					print(temp_segment)
					if (fetch_segments(temp_segment)) == "true":
						num_preflight_success += 1

	else:
		print("Preflight in single variant playlist...")
		print("Number of required successful preflight items: " + str(num_preflight_condition))
		if(check_playlist(user_hls_playlist)) == "true":
				num_preflight_success += 1
		temp_segment = baseurl +" ".join(map(str,segments_list[0])) + ".ts"
		print(temp_segment)
		if (fetch_segments(temp_segment)) == "true":
			num_preflight_success += 1
	logentry="#########################\nEnd of Preflight Check\n"
	f.write(logentry)	

#print("Enter URL of playlist:")
#user_hls_playlist=raw_input("Enter URL of playlist: ")

user_hls_playlist='http://qn-01038-comnet-poc-1.opencachehub.qwilted-cds.cqloud.com/soccer_barcelona_atletico_madrid_abr/480_2M/index.m3u8'
#user_hls_playlist='http://qn-01038-comnet-poc-1.opencachehub.qwilted-cds.cqloud.com/soccer_barcelona_atletico_madrid_abr/index.m3u8'

# Validate input URL as m3u8 playlist & retreive ABR resolutions
if check_playlist(user_hls_playlist) == "true":
	print("Input playlist is valid...")
	hls_playlist=m3u8.load(user_hls_playlist)
	if hls_playlist.is_variant:
		print("This is ABR playlist...")
		get_baseurl()
		temp_variant_playlist=baseurl+hls_playlist.playlists[0].uri
		print("Before entering get segments, variant url is:")
		print(temp_variant_playlist)
		get_segments(temp_variant_playlist)
		# Find all resolutions in the master playlist
		for playlist in hls_playlist.playlists:
			print(playlist.uri)
			r = re.findall("(.+?)/index\.m3u8",playlist.uri)
			if r:
				print(r)
				resolution_list.append(r)
				#print(playlist.stream_info.bandwidth)
		num_preflight_condition=len(resolution_list)*2
		check_preflight(hls_playlist.is_variant)
		print("The number of variant playlists is: "+str(len(resolution_list))+" and number of segments per playlist is: "+str(len(segments_list)))
		print("The number of successful preflight items completed: "+str(num_preflight_success))
	else:
		get_baseurl()
		get_segments(user_hls_playlist)
		num_preflight_condition=2 #<-------- hmmmmmm
		print("This is likely a single variant playlist...")
		print("The number of variant playlist is: 1 and number of segments per playlist is: "+str(len(segments_list)))
		check_preflight(hls_playlist.is_variant)
		print("The number of successful preflight items completed: "+str(num_preflight_success))
else:
	print("Input playlist is invalid. Exiting...")
	sys.exit()

if num_preflight_success == num_preflight_condition:
	print("All preflight conditions met, prefetch may continue...")
	choice_fetch = raw_input("Press (C) to continue with prefetch and (Q) to Quit: ")
	if choice_fetch == "C" or choice_fetch == "c":
		print("C is selected")
		### Continue with prefetching
	elif choice_fetch == "Q" or choice_fetch == "q":
		print("Q is selected")
	else:
		print("Not valid input...")
else:
	print("Preflight conditions not met, terminating...")
	sys.exit()

#print(hls_playlist.segments)
#print(hls_playlist.target_duration)
#print(hls_playlist.is_variant)
#print(resolution_list)
print("End of program")
#print(len(segments_list))
#print(len(resolution_list))

f.close()
