var config = {	
	HiGlassNewTrackCenter : {
		"type": "combined",
		"contents": [
			{
				"server": "/api/v1",
				"type": "heatmap",
				"options": {
					"backgroundColor": "#eeeeee",
					"labelPosition": "bottomRight",
					"labelLeftMargin": 0,
					"labelRightMargin": 0,
					"labelTopMargin": 0,
					"labelBottomMargin": 0,
					"labelShowResolution": true,
					"colorRange": [
						"white",
						"rgba(245,166,35,1.0)",
						"rgba(208,2,27,1.0)",
						"black"
					],
					"colorbarBackgroundColor": "#ffffff",
					"maxZoom": null,
					"colorbarPosition": "topRight",
					"trackBorderWidth": 0,
					"trackBorderColor": "black",
					"heatmapValueScaling": "log",
					"showMousePosition": false,
					"mousePositionColor": "#000000",
					"showTooltip": false,
					"extent": "full",
					"scaleStartPercent": "0.00000",
					"scaleEndPercent": "1.00000"
				},
				"width": 100,
				"height": 100,
				"transforms": [
					{
						"name": "ICE",
						"value": "weight"
					}
				],
				"resolutions": [
					10000,
					20000,
					40000,
					80000,
					160000,
					320000,
					640000,
					1280000,
					2560000,
					5120000,
					10240000
				]
			}
		],
		"options": {}
		},
	HiGlassNewTrack : {
		"server": "/api/v1",
		"options": {
			"labelColor": "black",
			"labelPosition": "topLeft",
			"labelLeftMargin": 0,
			"labelRightMargin": 0,
			"labelTopMargin": 0,
			"labelBottomMargin": 0,
			"labelBackgroundColor": "white",
			"labelShowResolution": false,
			"axisLabelFormatting": "scientific",
			"axisPositionHorizontal": "right",
			"lineStrokeColor": "blue",
			"lineStrokeWidth": 1,
			"valueScaling": "linear",
			"trackBorderWidth": 0,
			"trackBorderColor": "black",
			"labelTextOpacity": 0.4,
			"showMousePosition": false,
			"mousePositionColor": "#000000",
			"showTooltip": false,
		},
		"height" : 50,
	},
	HiGlassEmptyViewConfig: {
			"editable": true,
					"zoomFixed": false,
					"trackSourceServers": [
						"/api/v1",
					],
					"exportViewUrl": "/api/v1/viewconfs/",
					"views": [
						{
							"tracks": {
								"top": [],
								"left": [],
								"center": [],
								"right": [],
								"bottom": [],
								"whole": [],
								"gallery": []
							},
							"initialXDomain": [
								-3.725290298461914e-9,
								3199999999.999999
							],
							"initialYDomain": [
								394659170.76598734,
								2814335910.0491905
							],
							"layout": {
								"w": 12,
								"h": 12,
								"x": 0,
								"y": 0,
								"moved": false,
								"static": false
							},
							"uid": "Giu3hnavTBKhbPDDjCS8Xg",
							"genomePositionSearchBox": {
								"autocompleteServer": "/api/v1",
								"chromInfoServer": "/api/v1",
								"autocompleteId": "QDutvmyiSrec5nX4pA5WGQ"
							}
						}
					],
					"zoomLocks": {
						"locksByViewUid": {},
						"locksDict": {}
					},
					"locationLocks": {
						"locksByViewUid": {},
						"locksDict": {}
					},
					"valueScaleLocks": {
						"locksByViewUid": {},
						"locksDict": {}
					}
				},
		HiGlassNewAnnotationTrack : {
			"server": "/api/v1",
			"height": 60,
			"width": 60,
			"options": {
				"fontSize": 11,
				"labelColor": "black",
				"labelBackgroundColor": "#ffffff",
				"labelPosition": "hidden",
				"labelLeftMargin": 0,
				"labelRightMargin": 0,
				"labelTopMargin": 0,
				"labelBottomMargin": 0,
				"plusStrandColor": "blue",
				"minusStrandColor": "red",
				"trackBorderWidth": 0,
				"trackBorderColor": "black",
				"showMousePosition": false,
				"mousePositionColor": "#000000",
				"geneAnnotationHeight": 10,
				"geneLabelPosition": "outside",
				"geneStrandSpacing": 4,
			},
		}
}

export default config;
