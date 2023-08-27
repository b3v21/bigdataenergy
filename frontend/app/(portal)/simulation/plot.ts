import { PlotParams } from 'react-plotly.js';

const layout: PlotParams['layout'] = {
	dragmode: 'zoom',
	mapbox: {
		style: 'dark',
		center: { lat: -27.5, lon: 153 },
		zoom: 10
	},
	margin: { r: 0, t: 0, b: 0, l: 0 }
};

const data: PlotParams['data'] = [
	{
		type: 'scattermapbox',
		text: ['St Lucia Stop', 'Suncorp Stadium'],

		lon: [153.003065, 153.009596],
		lat: [-27.494233, -27.46487],
		marker: {
			size: 20,
			color: ['#bebada', '#bebada'],
			line: {
				width: 5
			}
		}
	}
];
export { data, layout };
