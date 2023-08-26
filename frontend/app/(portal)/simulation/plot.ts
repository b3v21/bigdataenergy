import { PlotParams } from 'react-plotly.js';

const layout: PlotParams['layout'] = {
	dragmode: 'zoom',
	mapbox: {
		style: 'dark',
		center: { lat: -27.5, lon: 153 },
		zoom: 9
	},
	margin: { r: 0, t: 0, b: 0, l: 0 }
};

const data: PlotParams['data'] = [
	{
		type: 'scattermapbox',
		text: [
			'Montreal',
			'Toronto',
			'Vancouver',
			'Calgary',
			'Edmonton',
			'Ottawa',
			'Halifax',
			'Victoria',
			'Winnepeg',
			'Regina'
		],

		lon: [
			-73.57, -79.24, -123.06, -114.1, -113.28, -75.43, -63.57, -123.21, -97.13,
			-104.6
		],
		lat: [45.5, 43.4, 49.13, 51.1, 53.34, 45.24, 44.64, 48.25, 49.89, 50.45],
		marker: {
			size: 7,
			color: [
				'#bebada',
				'#fdb462',
				'#fb8072',
				'#d9d9d9',
				'#bc80bd',
				'#b3de69',
				'#8dd3c7',
				'#80b1d3',
				'#fccde5',
				'#ffffb3'
			],
			line: {
				width: 1
			}
		}
	}
];
export { data, layout };
