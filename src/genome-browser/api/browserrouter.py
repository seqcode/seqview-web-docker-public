import logging;
from .models import Species, Genome, Expttype, Lab, Exptcondition, Expttarget, Cellline, Readtype, Aligntype, Seqexpt, Seqalignment, HiGlassFiles
logger = logging.getLogger(__name__)

class BrowserRouter:

    def db_for_read(self, model, **hints):


        if model._meta.db_table == "api_higlassfiles":
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        logger.warning(obj1._meta.db_table);
        logger.warning(obj2._meta.db_table);

        if obj1._meta.db_table == 'seqalignment' and obj2._meta.db_table == "api_higlassfiles":
            return True;
        return None

