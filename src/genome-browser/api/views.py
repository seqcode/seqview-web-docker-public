import logging;
import requests;
import re;
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
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse

# Input: A URI for a requested resource
# Output: An HttpResponse with the X-Accel-Redirect header set to the requested URI
#         Nginx sees this response and serves the requested URI.
def getXAccelRedirect(uri):
	response = HttpResponse()
	response['X-Accel-Redirect'] = uri
	response['Content-Type'] = ''
	return response

def fetchOneRow(queryStr, queryArgs):
	with connections['core'].cursor() as cursor:
		cursor.execute(queryStr, queryArgs);
		row = cursor.fetchone()
		if cursor.rowcount == 0:
			return []
		else:
			return row;


def fetchAll(queryStr, queryArgs):
	with connections['core'].cursor() as cursor:
		cursor.execute(queryStr, queryArgs);
		columns = [col[0] for col in cursor.description]
		return [
			dict(zip(columns, row))
			for row in cursor.fetchall()
		], cursor.rowcount;

# Input: A MySql query string and query arguments
# Output: Returns True if there is a row returned by the query. Returns False
#         otherwise. 	
def checkIsAuthorized(queryStr, queryArgs):
	with connections['core'].cursor() as cursor:
		cursor.execute(queryStr, queryArgs);
		row = cursor.fetchone()
		if cursor.rowcount == 0:
			return False
		else:
			return True

# Output: Returns an X-Accel-Redirect response for the given responseURL if the query
#         returns any rows. Arguments from the query are added to the responseURL if
#         useRowArgs is set to True.
def getValidatedResponse(queryStr, queryArgs, responseURL, useRowArgs):
	try:
		row = fetchOneRow(queryStr, queryArgs)
		if row != []:
			if useRowArgs == True:
				responseURL = responseURL.format(*row)
			return getXAccelRedirect(responseURL)
		else:
                        # Not found (or forbidden, but I don't see any
                        # reason to let the user know the resource
                        # exists but is forbidden)
			return HttpResponse(status=404)
	except:
		# Bad Request
		return HttpResponse(status=400)

# Output: Wildcard expression for permission args for the MySQL seqdata table. If the 
#         user for the request is authorized, then add permissions for that user.
def getPermissions(request):
	# duplicated so that number of query args for public and with username are the same
	permissions = ['public;%', '%;public;%', 'public;%', '%;public;%'];
	if request.user.is_authenticated:
		user = request.user.get_username()
		permissions = ['public;%', '%;public;%', user+';%', '%;' + user + ';%'];

	return permissions

def getHiGlassAnnQueryStr():
	return 'select * from seqdata.seqalignment as seqa join core.genome as gen on seqa.genome = gen.id join browserwebsite.api_higlassannotations as ann on ann.genome = gen.id where ann.higlass_UID = %s and (seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s)';

def adminPage(request):
	#return HttpResponse("Here")
	if request.user.is_superuser == False:
		return HttpResponse(403)
	return getXAccelRedirect("/upload/seqdata_query.cgi")
	
# Output: Returns X-Accel-Redirect to filename if user is authenticated for that
#         resource. Will return 400 error code for bad request or 404 if not found or
#         permission denied.
def getTrack(request, filename):
	user = request.user.get_username()
	is_annotation = False
	filetype = ""
	prefix = ""
	index = ""
	if "annotations" in request.path.split("/"):
		is_annotation = True
	if is_annotation == False:
		suffix = ""
		ID = re.split('[a-zA-Z.]+', filename)[0]# Match to number
		try:
			suffix_array = re.split('^[0-9]+', filename.split('.')[0])
			if suffix_array:
				if suffix_array[1].lower() == 'minusstrand':
					suffix = 'MinusStrand'
				if suffix_array[1].lower() == 'plusstrand':
					suffix = 'PlusStrand'
		except:
			return HttpResponse(400)
		responseURL ="/seqalignments/{0}" + suffix + ".bw?"+urlencode(request.GET);
		if request.user.is_authenticated:
			queryStr = 'select id from seqdata.seqalignment where id=%s and (permissions like %s or permissions like %s or permissions like %s or permissions like %s)';
		else:
			queryStr = 'select id from seqdata.seqalignment where id=%s and (permissions like %s or permissions like %s)';
		return getXAccelRedirect("/tracks/" + filename + "?"+urlencode(request.GET))
	else:
		ID = filename.split(".")[0];
		prefix = "annotation"
		if "index" in request.path.split("/"):
			index = ".tbi"
		responseURL ="/tracks/"+prefix+"{0}.{1}" + index + "?"+urlencode(request.GET);
		queryStr = 'select ann.id as id, annfe.name as fileext from seqdata.seqalignment as seqa join core.genome as gen on seqa.genome = gen.id join core.annotation as ann on ann.genome = gen.id join anntype as annty on ann.anntype = annty.id join core.annfileformat as annff on annty.fileformat = annff.id join core.annfileext as annfe on annff.fileext = annfe.id where ann.id = %s and (seqa.permissions like %s or seqa.permissions like %s)';
		if request.user.is_authenticated:
			queryStr = 'select ann.id as id, annfe.name as fileext from seqdata.seqalignment as seqa join core.genome as gen on seqa.genome = gen.id join core.annotation as ann on ann.genome = gen.id join anntype as annty on ann.anntype = annty.id join core.annfileformat as annff on annty.fileformat = annff.id join core.annfileext as annfe on annff.fileext = annfe.id where ann.id = %s and (seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s)';	
	if request.user.is_authenticated:
		queryArgs = [ID, 'public;%', '%;public;%', user+';%', '%;' + user + ';%'];
	else:
		queryArgs = [ID, 'public;%', '%;public;%'];
	useRowArgs = True;
	return getValidatedResponse(queryStr, queryArgs, responseURL, useRowArgs)
	 

class getAnnotations(viewsets.ViewSet):
	authentication_classes = [SessionAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]
	def list(self, request):
		queryArgs = getPermissions(request)
		queryStr = 'select ann.id, annty.name, gen.version as genome, annff.name as fileformat, annfe.name as fileext, CONCAT(gen.version, "refGene") as higlass_UID from annotation as ann join genome as gen on gen.id = ann.genome join anntype as annty on annty.id=ann.anntype join annfileformat as annff on annty.fileformat = annff.id join annfileext as annfe on annff.fileext = annfe.id join seqdata.seqalignment as seqa on gen.id = seqa.genome where permissions like %s or permissions like %s or permissions like %s or permissions like %s group by ann.id, annty.name, gen.version, annff.name, annfe.name, higlass_UID';
		response, rowCount = fetchAll(queryStr, queryArgs)
		return Response(response)

class getSeqalignments(viewsets.ViewSet):
	authentication_classes = [SessionAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]
	def list(self, request):
		user = request.user.get_username()
		with connections['core'].cursor() as cursor:
			cursor.execute('select seqa.id as id, gen.version as genome, exptty.name as expttype, clab.name as lab,' 
		'exptc.name as exptcondition, celll.name as cellline, seqa.name as alignment, seqe.replicate as replicate,'
		' exptta.name as expttarget, seqa.name as name, seqe.name as seqexptname,'
		' readt.name as readtype, seqe.readlength as readlen, seqe.numreads as numread, seqe.collabid as collabid,'
		 ' seqe.publicsource as publicsource, seqe.publicdbid as publicdbid, seqe.fqfile as fqfile,' 
		' seqe.exptnote as exptnote, seqa.numhits as numhits, seqa.totalweight as totalweight, seqa.aligndir as aligndir, seqa.alignfile as alignfile, seqa.idxfile as idxfile, seqa.collabalignid as collabalignid, alignt.name as aligntype from ' 
		'(seqdata.seqalignment seqa join seqdata.seqexpt seqe on seqa.expt = seqe.id) left join core.species spe'
		' on seqe.species = spe.id left join core.expttype exptty on seqe.expttype=exptty.id'
		' left join core.lab clab on seqe.lab=clab.id  left join core.exptcondition exptc'
		' on seqe.exptcondition=exptc.id left join core.expttarget exptta on seqe.expttarget='
		' exptta.id left join core.cellline celll on seqe.cellline=celll.id left join core.readtype readt'
		' on seqe.readtype=readt.id left join core.genome gen on seqa.genome=gen.id left join core.aligntype alignt'
		' on seqa.aligntype=alignt.id'
		' where wiguploadstatus="UPLOADED" and (seqa.permissions like "public;%%" or seqa.permissions like "%%;public;%%"'
		' or seqa.permissions like %s or seqa.permissions like %s)', [user + ';%', '%;' + user + ';%']);
			columns = [col[0] for col in cursor.description]
			return Response([
				dict(zip(columns, row))
				for row in cursor.fetchall()
			])


class getAvailableChromSizes(viewsets.ViewSet):
	authentication_classes = [SessionAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]
	def list(self, request):

		query_str = (' select gen.version as uuid, CONCAT(gen.version, ".tsv") as name, gen.version as coordSystem, gen.version as coordSystem2, "" as project_name, "" as project_owner, "" as description' 
		' from core.genome as gen join seqdata.seqalignment as seqa on gen.id = seqa.genome' 
		' where seqa.permissions like %s or seqa.permissions like %s'
		' or seqa.permissions like %s or seqa.permissions like %s' 
		' group by gen.version')
		chrom_sizes = dict()
		chrom_sizes["results"], chrom_sizes["count"] = fetchAll(query_str, getPermissions(request))
		return Response(chrom_sizes);

		
class ChromSizes(viewsets.ViewSet):
	authentication_classes = [SessionAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]
	def list(self, request):
		# Only accept a single id
		request_id = request.query_params.get('id')
		query_str = ('select gen.id as id, gen.version as version, spe.name as name'
				' from core.genome as gen join seqdata.seqalignment as seqa on gen.id = seqa.genome'
				' join core.species as spe on spe.id = gen.species'
		' where (seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s) and gen.version = %s'
		' group by gen.id')
		query_args = getPermissions(request) + [request_id]
		return getValidatedResponse(query_str, query_args, "/higlass/api/v1/chrom-sizes?id=" + request_id, False)

		
class TilesetInfo(viewsets.ViewSet):
	authentication_classes = [SessionAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]
	def list(self, request):
		username = request.user.get_username()
		queryStr = 'select * from browserwebsite.api_higlassfiles as hig join seqdata.seqalignment as seqa on hig.seqalignment = seqa.id where hig.tilesetUID = %s and (seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s)';
		annotationQueryStr = 'select * from seqdata.seqalignment as seqa join core.genome as gen on seqa.genome = gen.id join browserwebsite.api_higlassannotations as ann on ann.genome = gen.id where ann.higlass_UID = %s and (seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s)'; 
		
		tilesetUID = request.query_params.get('d')
		queryArgs = [tilesetUID] + getPermissions(request);
		annotationQueryArgs = [tilesetUID] + getPermissions(request);
		chromsizesQueryStr = (' select hig.uuid' 
		' from core.genome as gen join seqdata.seqalignment as seqa on gen.id = seqa.genome' 
		' join core.species as spe on spe.id = gen.species join browserwebsite.api_higlasschromsizes as hig on gen.version = hig.coordsystem' 
		' where (seqa.permissions like %s or seqa.permissions like %s'
		' or seqa.permissions like %s or seqa.permissions like %s)'
		' and hig.uuid = %s' 
		' group by hig.uuid, hig.name, hig.coordsystem, hig.coordsystem2, hig.project_name, hig.project_owner, hig.description')
		chromsizesQueryArgs = getPermissions(request) + [tilesetUID]
		#if checkIsAuthorized(queryStr, queryArgs) == False and checkIsAuthorized(annotationQueryStr, annotationQueryArgs) == False and checkIsAuthorized(chromsizesQueryStr, chromsizesQueryArgs) == False:
		#	return HttpResponse(status=404);
		return getXAccelRedirect("/higlass/api/v1/tileset_info?{0}".format(request.query_params.urlencode()))


class Tiles(viewsets.ViewSet):
	authentication_classes = [SessionAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]
	def list(self, request):
		username = request.user.get_username()
		queryStr = 'select * from browserwebsite.api_higlassfiles as hig join seqdata.seqalignment as seqa on hig.seqalignment = seqa.id where hig.tilesetUID = %s and (seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s)';
		annotationQueryStr = 'select * from seqdata.seqalignment as seqa join core.genome as gen on seqa.genome = gen.id join browserwebsite.api_higlassannotations as ann on ann.genome = gen.id where ann.higlass_UID = %s and (seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s)'; 
		
		for d in request.query_params.getlist('d'):
			tilesetUID = d.split('.')[0];
			queryArgs = [tilesetUID] + getPermissions(request);
			annotationQueryArgs = [tilesetUID] + getPermissions(request);
			#if checkIsAuthorized(queryStr, queryArgs) == False and checkIsAuthorized(annotationQueryStr, annotationQueryArgs) == False:
			#	return HttpResponse(status=404);
		return getXAccelRedirect("/higlass/api/v1/tiles?{0}".format(request.query_params.urlencode()))


class RegisterURL(viewsets.ViewSet):
	authentication_classes = [SessionAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]
	def put(self, request, *args, **kwargs):
		username = request.user.get_username()
		d = request.query_params.get('d');
		return HttpResponse("Done")	
		return getXAccelRedirect("/higlass/api/v1/register_url?{0}".format(request.query_params.urlencode()))
	def list(self, request):
		return HttpResponse("Hi")

class Tilesets(viewsets.ViewSet):
	authentication_classes = [SessionAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]
	def list(self, request):
		username = request.user.get_username()

		queryStr = (' select CONCAT(gen.version, "refGene") as uuid, "" as datafile, "beddb" as filetype, "gene-annotation" as datatype, CONCAT(CONCAT("gene-annotations-", gen.version), ".db") as name, gen.version as coordSystem, gen.version as coordSystem2, "" as project, "" as project_name, "" as description' 
		' from core.genome as gen join seqdata.seqalignment as seqa on gen.id = seqa.genome' 
		' where seqa.permissions like %s or seqa.permissions like %s'
		' or seqa.permissions like %s or seqa.permissions like %s' 
		' group by gen.version')
		queryArgs = getPermissions(request);
		response = dict()
		response["results"], response["count"] = fetchAll(queryStr, queryArgs)
		response["next"] = "null"
		response["previous"] = "null"
		return Response(response)

class Suggest(viewsets.ViewSet):
	authentication_classes = [SessionAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]
	def list(self, request):
		username = request.user.get_username()
		try:
			browser = request.query_params.get('browser', "higlass")
		except:
			browser = "higlass"
		#return HttpResponse(browser.lower())
		if browser.lower() == "igv":
			genomeQueryStr = "select gen.version from core.genome as gen join seqdata.seqalignment as seqa on seqa.genome = gen.id where (seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s) and gen.version = %s limit 1;"
			genomeQueryArgs = getPermissions(request) + [request.query_params.get('genome')]
			genomeResponse = fetchOneRow(genomeQueryStr, genomeQueryArgs)
			if not genomeResponse:
				return Response([])
			genome = genomeResponse[0]  
			name = request.query_params.get('name')
			queryStr="select chrom as chr, txStart, txEnd, name2 as name from ucsc_" + genome + ".refGene where name2 like %s"
			queryArgs=[name + '%']
			try:
				response, rowcount = fetchAll(queryStr, queryArgs)
				return Response(response)
			except:
				return Response("Failed to get gene name for assembly. Is assembly loaded in database?")

		else:
			queryStr = getHiGlassAnnQueryStr()
			tilesetUID = request.query_params.get('d')
			ac = request.query_params.get('ac')
			#return HttpResponse(queryStr)
			queryArgs = [tilesetUID] + getPermissions(request);
			return getValidatedResponse(queryStr, queryArgs, "/higlass/api/v1/suggest?d={0}&ac={1}".format(tilesetUID, ac), False)

class getHiGlassFilesViewSet(viewsets.ModelViewSet):
	authentication_classes = [SessionAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]
	queryset = HiGlassFiles.objects.all();
	serializer_class = HiGlassFilesSerializer


class getAssemblies(viewsets.ViewSet):
	authentication_classes = [SessionAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]
	def list(self, request):
		with connections['core'].cursor() as cursor:
			user = request.user.get_username()
			queryStr = ('select gen.id as id, gen.version as version, spe.name as name'
				' from core.genome as gen join seqdata.seqalignment as seqa on gen.id = seqa.genome'
				' join core.species as spe on spe.id = gen.species'
		' where seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s or seqa.permissions like %s'
		' group by gen.id')
			queryArgs = getPermissions(request);
			response, rowCount = fetchAll(queryStr, queryArgs) 
			return Response(response)

class postTrack(viewsets.ViewSet):
	authentication_classes = [SessionAuthentication, BasicAuthentication]
	permission_classes = [IsAuthenticated]
	def put(self, request, *args, **kwargs):
		user = request.user.get_username()
		if user == 'mahonylab':
			row = ingestTrack()
			return Response(row)
		else:
			return HttpResponse(status=404)

