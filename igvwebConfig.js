var igvwebConfig = {
    genomes: "resources/genomes.json",
    trackRegistryFile: "resources/tracks/trackRegistry.json",
	//clientId: "848618608589-8s3dkha1lhh2gh5isgf7d2376e0ngkp3.apps.googleusercontent.com",
    igvConfig:
        {
			genomeList: "resources/genomes.json",
            queryParametersSupported: true,
            showChromosomeWidget: true,
            genome: "hg19",
            showSVGButton: false,
            search: {
                    url: "https://seqview.psu.edu/api/v1/suggest/?genome=$GENOME$&name=$FEATURE$&browser=IGV",
                    chromosomeField: "chr",
                    startField: "txStart",
                    endField: "txEnd",
						
                    },
			//apiKey: "AIzaSyCQvcYRP0cWogQQA28iGX3mQMvpZPN5VQM",
            tracks: [
                // TODO -- add default tracks here.  See github.com/igvteam/igv.js/wiki for details
                // {
                //     name: "CTCF - string url",
                //     type: "wig",
                //     format: "bigwig",
                //     url: "https://www.encodeproject.org/files/ENCFF563PAW/@@download/ENCFF563PAW.bigWig"
                // }
            ]
        },

    // Provide a URL shorterner function or object.   This is optional.  If not supplied
    // sharable URLs will not be shortened .
    urlShortener: {
        provider: "tinyURL"
    }
};
