# Introduction

This document describes the setup for seqview web. It contains information about adding new files and common tasks associates with seqview web.

## Adding a new genome to IGV

To add a new genome, you need to add fasta files for the genome to the PASS space /tracks in the following format:

```
<genome>.fa
<genome>.fa.tbi
```
Then, update the genome table in the core mysql database

## Adding a new annotation to IGV

### Gff3 pre-processing steps

For repeat masker and gencode genes in gff3 format, the files are too large to load directly in the browser. Therefore, we will have to create an index file. The first step in doing this is to sort the file. To do this for gff3, I used igvtools:

```
igvtools sort <genome>.gff3 <genome>.sorted.gff3
```

Then, I indexed the file using tabix:

```
tabix -p gff3 <genome>.sorted.gff3
```

### Repeat masker files

For repeat masker files, I just grabbed these from igv. To do this, open up the IGV webapp. Then, open up the developer tools in your browser. Load a repeat masker track in IGV. Find the corresponding URL added by IGV for the file and its index and download both. 

### Uploading Annotations to PASS and Adding an Entry to MySQL

For Refseq Genes and CpG island annotations, they are small enough to not need sorting and indexing. The next step for gff3, RefSeq genes and CpG island annotations, is to bgzip the file:

```
bgzip -c <file> > <file>.gz
```

Add the file to the PASS space in the following format depending on the annotation type:

```
<genome>refgene.txt.gz
<genome>cpgislandext.txt.gz
<genome>gff3.gff3.gz
<genome>gff3.gff3.gz.tbi
<genome>rmsk.txt.gz
<genome>rmsk.txt.gz.tbi
```

For example, for hg19 RefSeq genes the filename would be:

```
hg19refgene.txt.gz
```

PASS is mounted to the banba server at /pass-smb/services/www/dept/mahonylab/tracks. Ask Shaun for access to banba. Lastly, add the annotation to the mysql core database on the banba server (this table should be added to lugh soon if it isn't already there). First, find your annotation type with:

```
select * from anntype;
```

If it doesn't already exist, create the corresponding entries in the anntype and annfileformat tables. Then,

```
insert annotation (genome, anntype) values (<genome>, <anntype>);
```
## Adding Genome/Annotation to HiGlass

Log on to the banba server as the higbanb user. Put a tab-delimited chromosome sizes file and annotations in the following format in the folder:

```
cp <genome>.info data/media/<genome.info
cp gene-annotations-<genome>.db data/media/gene-annotations-<genome>.db
```

Annotations must be in Higlass format. See [Making HiGlass Annotations](#making-higlass-annotations). To add a genome:

```
source higlass-server-env/bin/activate
python higlass-server/manage.py ingest_tileset --filetype chromsizes-tsv --datatype chromsizes --coordSystem $genome --coordSystem2 $genome --filename $genome.tsv --no-upload --uid $genome
```

To add an annotation:

```
source higlass-server-env/bin/activate
python higlass-server/manage.py ingest_tileset --filename gene-annotations-$genome.db --filetype beddb --datatype geneannotation --coordSystem $genome --coordSystem2 $genome --uid ${genome}refGene --no-upload
```

## Making HiGlass Annotations

Log on to ACI. You will need the Clodius package installed:

```
pip install clodius
```

Copy the code in:

```
~/group/genomes/mm10_synHoxA/annotation/higlass_annotations
```

To whatever directory you are creating the annotation in. Download the following files into the data/ directory:

```
wget ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2refseq.gz
wget ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz
wget ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2pubmed.gz
```

If you are adding custom genes, follow the format of the files in the data/ directory:

```
addl_gene2pubmed,addl_gene2refseq,addl_gene_info
```

Then, run,

```
sh data/fake_adds.sh
```

Modify the genome and taxid at the top of

```
refgene_to_higlass_modified.sh
```

Then, run that command. If you don't need to add custom genes, you can skip those steps and just modify the genome and taxid of

```
refgene_to_higlass.sh
```

and run the command. The outputted annotation will be in data/<genome>/gene-annotations-<genome>.db

## Adding an Mcool file to HiGlass

Login to the banba server as the higbanb user. Copy the file to the data/media folder with the following naming convention:

```
cp <seqid>.mcool data/media/<seqid>.mcool
source higlass-server-env/bin/activate
cd higlass-server
python manage.py ingest_tileset --filename <seqid>.mcool --no-upload --filetype cooler --datatype matrix --coordSystem <genome> --coordSystem2 <genome> --uid <seqid>
```

## Seqview overview

![Alt text](images/seqview.jpg?raw=true "SeqView Overview")

## Seqview Python Web Application 

The seqview python web application is run as the genomebrowser user using gunicorn. Gunicorn is started as a systemd service. The unit definition for the service is at:

```
/etc/systemd/system/seqview.service
```

If you need to modify this file, after any modification run:

```
sudo systemctl daemon-reload
```

If the service is not running after this, you can run:

```
sudo systemctl start seqview.service
```

Environmental variables for gunicorn are stored in:

```
/etc/sysconfig/seqview
```

This includes the mysql password. Log files generated by gunicorn can be found at:

```
/var/log/seqview/access.log
/var/log/seqview/error.log
```

Errors might also appear in the service log. Check:

```
journalctl -u seqview
```

## HiGlass Server Application

The unit definition for the service is at:

```
/etc/systemd/system/higlass.service
```

Environmental variables for gunicorn are stored in:

```
/etc/sysconfig/higlass
```

Log files can be found at:

```
/home/higlass/data/log/hgs.log
```


## Web Server and Wig Upload Script Accessing PASS Space

The PASS storage space is mounted as an NFS filesystem at /pass on banba. PASS uses Kerberos for authentication on the NFS mount. There are two applications which need to access PASS on banba: Nginx and the wig exporter script which is part of the alignment pipeline (HiGlass accesses PASS through HTTP requests to the Nginx server). For this, there are two service accounts registered to access PASS: ngnxban, and higbanb. Kerberos credentials expire after a fixed time. To ensure that credentials are constantly refreshed, k5start is run as two systemd services. The k5start scripts are located at:

```
/etc/systemd/system/k5start-higbanb.service
/etc/systemd/system/k5start-nginx.service
```

These k5start scripts use a set Kerberos cache file. For nginx, there is an environment variable in its configuration script which sets the kerberos cache file to use. For the wig exporter script, the environmental variable is set in higbanb's .bashrc file on banba.

## Upload Webpage for Sequencing

There is a Perl CGI script which is used for uploading sequencing sample sheets. On banba, the page is served by spawn-fcgi which is run as a service. You will also need fastcgi installed. The config file for spawn-fcgi is at:

````
/etc/sysconfig/spawn-fcgi
````

## Troubleshooting

If there are issues with seqview, the first step is to open seqview in a browser with the development tools tab open. If there is a network error, such as a url not loading, then I would check the nginx logs on banba. They are located at:

```
/var/log/nginx/error.log
/var/log/nginx/access.log
```

If they suggest the error is with the seqview python web application, look at the seqview logs. Information on where to find those is in the [seqview python](#seqview-python-web-application) section. If the error is with higlass, look at the higlass logs, information on where to find those in the [higlass](#higlass-server-application) section


