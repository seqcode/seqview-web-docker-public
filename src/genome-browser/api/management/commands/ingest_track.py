from django.db import connections
from django.core.management.base import BaseCommand

def ingestTrack(seqalignment, loadmultistrands, **ignored):
	with connections['core'].cursor() as cursor:
		queryStr = 'insert into browserwebsite.api_loadmultistrands (seqalignment, loadmultistrands) values (%s, %s);'
		queryArgs = [seqalignment, loadmultistrands]
		cursor.execute(queryStr, queryArgs);
		row = cursor.fetchone()
		return seqalignment, loadmultistrands

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('--seqalignment', type=int)
		parser.add_argument('--loadmultistrands', type=bool)

	def handle(self, *args, **options):
		print(ingestTrack(**options))
