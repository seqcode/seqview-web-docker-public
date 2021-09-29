import logging;
from urllib.parse import urlencode
from django.db import connections
from django.shortcuts import render
from django.template import loader
from django.db.models import F
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import AssembliesSerializer, SeqalignmentSerializer, HiGlassFilesSerializer
from .models import Species, Genome, Expttype, Lab, Exptcondition, Expttarget, Cellline, Readtype, Aligntype, Seqexpt, Seqalignment, HiGlassFiles
logger = logging.getLogger(__name__)
# Create your views here.

from django.http import JsonResponse, HttpResponse

def getXAccelRedirect(uri):
	response = HttpResponse()
	#response['Cookie'] = ""
	response['X-Accel-Redirect'] = uri
	response.set_cookie("")
	return response

def checkIsAuthorized(queryStr, queryArgs):
	with connections['core'].cursor() as cursor:
		cursor.execute(queryStr, queryArgs);
		row = cursor.fetchone()
		if cursor.rowcount == 0:
			return False
		else:
			return True

def getValidatedResponse(queryStr, queryArgs, responseURL):
	try:
		if checkIsAuthorized(queryStr, queryArgs) == True:
			return getXAccelRedirect(responseURL)
		else:
                        # Not found (or forbidden, but I don't see any
                        # reason to let the user know the resource
                        # exists but is forbidden)
                        return HttpResponse(status=404)
	except:
		# Bad Request
		return HttpResponse(status=400)
	
	
def validateURL(request, filename):

	seqalignID = filename.split(".")[0];
	queryStr = 'select * from seqdata.seqalignment where id=%s and (permissions like %s or permissions like %s)';
	queryArgs = [seqalignID, 'public;%', '%;public;%'];
	responseURL = "/tracks/{0}.bw?{1}".format(seqalignID, urlencode(request.GET))
	return getValidatedResponse(queryStr, queryArgs, responseURL)
	 

class getAnnotations(viewsets.ViewSet):
	def list(self, request):
		with connections['core'].cursor() as cursor:
			cursor.execute('select ann.id, ann.name, gen.version from annotation as ann join genome as gen on gen.id = ann.genome');
			columns = [col[0] for col in cursor.description]
			return Response([
				dict(zip(columns, row))
				for row in cursor.fetchall()
			])

class getSeqalignments(viewsets.ViewSet):
	#authentication_classes = [SessionAuthentication, BasicAuthentication]
	#permission_classes = [IsAuthenticated]
	def list(self, request):
		with connections['core'].cursor() as cursor:
			cursor.execute('select seqa.id as id, gen.version as genome, exptty.name as expttype, clab.name as lab,' 
		'exptc.name as exptcondition, celll.name as cellline, seqa.name as alignment, seqe.replicate as replicate,'
		' exptta.name as expttarget, hig.tilesetUID as higlassfiles, seqa.name as name from' 
		'(seqdata.seqalignment seqa join seqdata.seqexpt seqe on seqa.expt = seqe.id) left join core.species spe'
		' on seqe.species = spe.id left join core.expttype exptty on seqe.expttype=exptty.id'
		' left join core.lab clab on seqe.lab=clab.id  left join core.exptcondition exptc'
		' on seqe.exptcondition=exptc.id left join core.expttarget exptta on seqe.expttarget='
		' exptta.id left join core.cellline celll on seqe.cellline=celll.id left join core.readtype readt'
		' on seqe.readtype=readt.id left join core.genome gen on seqa.genome=gen.id left join core.aligntype alignt'
		' on seqa.aligntype=alignt.id left join browserwebsite.genomeTrackSidebar_higlassfiles hig on hig.seqalignment = seqa.id'
		' where seqa.permissions like "public;%" or seqa.permissions like "%;public;%"');
			columns = [col[0] for col in cursor.description]
			return Response([
				dict(zip(columns, row))
				for row in cursor.fetchall()
			])


class getAvailableChromSizes(viewsets.ViewSet):
	#authentication_classes = [SessionAuthentication, BasicAuthentication]
	#permission_classes = [IsAuthenticated]
	def list(self, request):
		#return Response({"User" : request.user.username});
		return getXAccelRedirect("/api/v1/available-chrom-sizes/");

class ChromSizes(viewsets.ViewSet):
	#authentication_classes = [SessionAuthentication, BasicAuthentication]
	#permission_classes = [IsAuthenticated]
	def list(self, request):
		return getXAccelRedirect("/api/v1/chrom-sizes/?{0}".format(urlencode(request.query_params)))

		
class TilesetInfo(viewsets.ViewSet):
	#authentication_classes = [SessionAuthentication, BasicAuthentication]
	#permission_classes = [IsAuthenticated]
	def list(self, request):
		#return HttpResponse(request.COOKIES)
		return getXAccelRedirect("/api/v1/tileset_info/?{0}".format(urlencode(request.query_params)))


class Tiles(viewsets.ViewSet):
	#authentication_classes = [SessionAuthentication, BasicAuthentication]
	#permission_classes = [IsAuthenticated]
	def list(self, request):
		username = 'public'
		queryStr = 'select * from browserwebsite.genomeTrackSidebar_higlassfiles as hig join seqdata.seqalignment as seqa on hig.seqalignment = seqa.id where hig.tilesetUID = %s and (seqa.permissions like %s or seqa.permissions like %s)';
		for d in request.query_params.getlist('d'):
			tilesetUID = d.split('.')[0];
			queryArgs = [tilesetUID, username + ';%', '%;' + username + 'public;%'];
			if checkIsAuthorized(queryStr, queryArgs) == False:
				return HttpResponse(status=404);
		return getXAccelRedirect("/api/v1/tiles/?{0}".format(request.query_params.urlencode()))


class Tilesets(viewsets.ViewSet):
	#authentication_classes = [SessionAuthentication, BasicAuthentication]
	#permission_classes = [IsAuthenticated]
	def list(self, request):
		return getXAccelRedirect("/api/v1/tilesets/?{0}".format(request.query_params.urlencode()))




class getHiGlassFilesViewSet(viewsets.ModelViewSet):
	#authentication_classes = [SessionAuthentication, BasicAuthentication]
	#permission_classes = [IsAuthenticated]
	queryset = HiGlassFiles.objects.all();
	serializer_class = HiGlassFilesSerializer

# class getSeqalignmentsViewSet(viewsets.ModelViewSet):
#     authentication_classes = [SessionAuthentication, BasicAuthentication]
#     permission_classes = [IsAuthenticated]
# 	queryset = Seqalignment.objects.raw('select * from' 
# 		'(seqdata.seqalignment seqa join seqdata.seqexpt seqe on seqa.expt = seqe.id) join core.species spe'
# 		' on seqe.species = spe.id join core.expttype exptty on seqe.expttype=exptty.id'
# 		' join core.Lab clab on seqe.lab=clab.id  join core.exptcondition exptc'
# 		' on seqe.exptcondition=exptc.id join core.expttarget exptta on seqe.expttarget='
# 		' exptta.id join core.cellline celll on seqe.cellline=celll.id join core.readtype readt'
# 		' on seqe.readtype=readt.id join core.genome gen on seqa.genome=gen.id join core.aligntype alignt'
# 		' on seqa.aligntype=alignt.id left join browserwebsite.genomeTrackSidebar_higlassfiles hig on hig.seqalignment = seqa.id')
# 	#queryset = Seqalignment.objects.select_related('expt').prefetch_related('expt__expttype', 'genome', 'expt__lab', 'expt__cellline', 'aligntype', 'expt__expttarget').all();
# 	serializer_class = SeqalignmentSerializer	

class getAssemblies(viewsets.ViewSet):
	#authentication_classes = [SessionAuthentication, BasicAuthentication]
	#permission_classes = [IsAuthenticated]
	def list(self, request):
		with connections['core'].cursor() as cursor:
			cursor.execute('select gen.id as id, gen.version as version, spe.name as name'
				' from core.genome as gen join seqdata.seqalignment as seqa on gen.id = seqa.genome'
				' join core.species as spe on spe.id = gen.species'
		' where seqa.permissions like "public;%" or seqa.permissions like "%;public;%"'
		' group by gen.id');
			columns = [col[0] for col in cursor.description]
			return Response([
				dict(zip(columns, row))
				for row in cursor.fetchall()
			])
#class getAssemblyViewSet(viewsets.ModelViewSet):
	# authentication_classes = [SessionAuthentication, BasicAuthentication]
	# permission_classes = [IsAuthenticated]
	#queryset = Genome.objects.all()
	#serializer_class = AssembliesSerializer
# def getAssemblies(request):
	# assemblies = Genome.objects.all().values('id', 'version', 'species__name')
	# context = {
	# 	'assemblies': list(assemblies)
	# }
	# return JsonResponse(context);
