from django.db import models
from .spanningfields import SpanningForeignKey, SpanningOneToOneField
# Create your models here.

class Aligntype(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'aligntype'


class Cellline(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'cellline'


class Chromosome(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    genome = models.ForeignKey('Genome', models.DO_NOTHING, db_column='genome')

    class Meta:
        managed = False
        db_table = 'chromosome'
        unique_together = (('name', 'genome'),)


class Exptcondition(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'exptcondition'


class Expttarget(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'expttarget'


class Expttype(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'expttype'


class Genome(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    species = models.ForeignKey('Species', models.DO_NOTHING, db_column='species')
    version = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'genome'
        unique_together = (('species', 'version'),)


class Lab(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'lab'


class Readtype(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'readtype'


class Seqdatauser(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=50)
    admin = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seqdatauser'


class Species(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=80)

    class Meta:
        managed = False
        db_table = 'species'


class Seqexpt(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    replicate = models.CharField(max_length=200)
    species = SpanningForeignKey('Species', models.DO_NOTHING, db_column='species')
    expttype = SpanningForeignKey('Expttype', models.DO_NOTHING, db_column='expttype')
    lab = SpanningForeignKey('Lab', models.DO_NOTHING, db_column='lab')
    exptcondition = SpanningForeignKey('Exptcondition', models.DO_NOTHING, db_column='exptcondition')
    expttarget = SpanningForeignKey('Expttarget', models.DO_NOTHING, db_column='expttarget')
    cellline = SpanningForeignKey('Cellline', models.DO_NOTHING, db_column='cellline')
    readtype = SpanningForeignKey('Readtype', models.DO_NOTHING, db_column='readtype')
    readlength = models.IntegerField()
    numreads = models.IntegerField(blank=True, null=True)
    collabid = models.CharField(max_length=200, blank=True, null=True)
    publicsource = models.CharField(max_length=200, blank=True, null=True)
    publicdbid = models.CharField(max_length=200, blank=True, null=True)
    fqfile = models.CharField(max_length=500, blank=True, null=True)
    exptnote = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seqexpt'
        unique_together = (('name', 'replicate'),)

class Seqalignment(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    expt = models.ForeignKey('Seqexpt', models.DO_NOTHING, db_column='expt')
    name = models.CharField(max_length=200)
    genome = SpanningForeignKey('Genome', models.DO_NOTHING, db_column='genome')
    permissions = models.CharField(max_length=500)
    aligntype = SpanningForeignKey('Aligntype', models.DO_NOTHING, db_column='aligntype')
    numhits = models.IntegerField(blank=True, null=True)
    totalweight = models.FloatField(blank=True, null=True)
    numtype2hits = models.IntegerField(blank=True, null=True)
    totaltype2weight = models.FloatField(blank=True, null=True)
    numpairs = models.IntegerField(blank=True, null=True)
    totalpairweight = models.FloatField(blank=True, null=True)
    aligndir = models.CharField(max_length=400, blank=True, null=True)
    alignfile = models.CharField(max_length=500, blank=True, null=True)
    idxfile = models.CharField(max_length=400, blank=True, null=True)
    collabalignid = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seqalignment'

class Annotation(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=50)
    genome = models.ForeignKey('Genome', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'annotation'


class HiGlassFiles(models.Model):
	id = models.AutoField(primary_key=True)
	seqalignment = SpanningOneToOneField('Seqalignment', models.DO_NOTHING, db_column='seqalignment')
	tilesetUID = models.CharField(max_length=40)


