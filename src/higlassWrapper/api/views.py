from rest_framework.parsers import FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import subprocess
import re
import os

class Track(APIView):
	permission_classes = (IsAuthenticated,)
	parser_classes = [FormParser]
	def post(self, request):
		#print(request.data)
		try:
			uid = request.data['uid']
			print(uid)
			genome = request.data['genome']
			print(genome)
			# Check if formatted correctly
			ID = re.split('[a-zA-Z.]+', uid)[0]# Match to number
			suffix_array = re.split('^[0-9]+', uid)
			suffix = ""
			if suffix_array:
				if suffix_array[1].lower() == 'minusstrand':
					suffix = 'MinusStrand'
				if suffix_array[1].lower() == 'plusstrand':
					suffix = 'PlusStrand'
			if suffix != "" and suffix != "MinusStrand" and suffix != "PlusStrand":
				return Response("Invalid uid") 
		except:
			return HttpResponse(400)
		hostname = os.environ['MACHINE_HOSTNAME']
		completed = subprocess.run(["python", "/home/higlass/projects/higlass-server/manage.py", "ingest_tileset", "--filename",  uid + ".bw", "--no-upload", "--filetype", "bigwig", "--coordSystem", genome, "--uid", ID + suffix], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
		return Response(completed.stdout)


