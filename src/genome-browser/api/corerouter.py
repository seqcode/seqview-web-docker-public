import logging;
from .models import Species, Genome, Expttype, Lab, Exptcondition, Expttarget, Cellline, Readtype, Aligntype, Seqexpt, Seqalignment, HiGlassFiles, Annotation
logger = logging.getLogger(__name__)

class CoreRouter:
    core = [table.lower() for table in ['Expttype', 'Lab', 'Exptcondition', 'Expttarget', 'Cellline', 'Readtype', 'Aligntype', 'Species', 'Genome', 'Annotation']]

    def db_for_read(self, model, **hints):

        if model._meta.db_table in self.core:
            return 'core'
        return None


