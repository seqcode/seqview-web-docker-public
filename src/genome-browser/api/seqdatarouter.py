import logging;
from .models import Species, Genome, Expttype, Lab, Exptcondition, Expttarget, Cellline, Readtype, Aligntype, Seqexpt, Seqalignment, HiGlassFiles
logger = logging.getLogger(__name__)

class SeqdataRouter:
    seqdata = [table.lower() for table in ['Seqalignment', 'Seqexpt']]

    def db_for_read(self, model, **hints):

        if model._meta.db_table in self.seqdata:
            return 'seqdata'
        return None


