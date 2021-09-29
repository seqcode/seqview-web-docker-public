from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import argparse
import configparser

def main():
	parser = argparse.ArgumentParser(description="Post ingest tileset request to higlass")
	parser.add_argument('--genome', action="store", dest="genome", default='', help="genome version")
	parser.add_argument('--uuid', action="store", dest="uuid", default='', help="higlass tileset uuid")
	args = parser.parse_args()
	post(**vars(args))
	#post(**args)
	
def post(genome, uuid):
	config = configparser.ConfigParser()
	config.read('post.ini')	
	r = Request("http://127.0.0.1:9000/api/api-token-auth/", urlencode({'username': config['Credentials']['username'], 'password' : config['Credentials']['password']}).encode())
	response = urlopen(r).read().decode()
	response_json = json.loads(response)
	postTrack = Request("http://127.0.0.1:9000/api/", urlencode({'genome': genome, 'uid' : uuid}).encode())
	postTrack.add_header('Authorization', "Token " + response_json['token'])
	response = urlopen(postTrack).read().decode()
	response_json = json.loads(response)
	print(response_json)

main()
