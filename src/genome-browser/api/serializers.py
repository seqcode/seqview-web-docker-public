from .models import Species, Genome, Expttype, Lab, Exptcondition, Expttarget, Cellline, Readtype, Aligntype, Seqexpt, Seqalignment, HiGlassFiles
from rest_framework import serializers


class SeqalignmentSerializer(serializers.ModelSerializer):
	expttype = serializers.StringRelatedField(source="expt.expttpe.name", read_only=True)
	genome = serializers.StringRelatedField(source="genome.version", read_only=True)
	lab = serializers.StringRelatedField(source="expt.lab.name", read_only=True)
	exptcondition = serializers.StringRelatedField(source="expt.exptcondition.name", read_only=True)
	cellline = serializers.StringRelatedField(source="expt.cellline.name", read_only=True)
	alignment = serializers.StringRelatedField(source="aligntype.name", read_only=True)
	replicate = serializers.StringRelatedField(source="expt.replicate", read_only=True)
	expttarget = serializers.StringRelatedField(source="expt.expttarget.name", read_only=True)
	higlassfiles = serializers.SlugRelatedField(read_only=True, slug_field='tilesetUID')
	class Meta:
		model = Seqalignment;
		depth = 1;
		fields = ('id',
				'genome',
				'expttype',
				'lab',
				'expttarget',
				'exptcondition',
				'cellline',
				'alignment',
				'replicate',
				'higlassfiles',
			)

class HiGlassFilesSerializer(serializers.ModelSerializer):
	class Meta:
		model = HiGlassFiles;
		depth = 1;
		fields = '__all__';

class AssembliesSerializer(serializers.ModelSerializer):
	name = serializers.StringRelatedField(source="species.name", read_only=True)
	class Meta:
		model = Genome;
		depth = 1;
		fields = ('id',
			'version',
			'name');
# class AssembliesSerializer(serializers.ModelSerializer):
# 	# class Meta:
# 	# 	model = Species;
# 	# 	depth = 1;
# 	# 	fields = '__all__';
# 	genome_set = serializers.SlugRelatedField(many=True, read_only=True, slug_field='version')
# 	class Meta:
# 		model = Species;
# 		depth = 1;
# 		fields = (
# 			'id',
# 			'name',
# 			'genome_set',)



	