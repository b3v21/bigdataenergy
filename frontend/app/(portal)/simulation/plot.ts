import { PlotParams } from 'react-plotly.js';

const layout: PlotParams['layout'] = {
	dragmode: 'zoom',
	mapbox: {
		style: 'dark',
		center: { lat: -27.5, lon: 153 },
		zoom: 12
	},
	margin: { r: 0, t: 0, b: 0, l: 0 }
};

const data: PlotParams['data'] = [
	{
		name: 'Bus',
		type: 'scattermapbox',
		lon: [153.003065, 153.009596, 153.033896],
		lat: [-27.494233, -27.46487, -27.455828],
		mode: 'lines+markers',
		text: ['St Lucia Stop', 'Suncorp Stadium'],
		showlegend: false,
		line: {
			width: 4,
			dash: 'dash',
			color: '#22c55e'
		},
		marker: {
			size: 12,
			color: ['#22c55e', '#ef4444', '#ef4444']
		}
	}
	// {
	// 	type: 'scattermapbox',
	// 	text: ['St Lucia Stop', 'Suncorp Stadium'],
	// 	lon: [153.003065, 153.009596],
	// 	lat: [-27.494233, -27.46487],
	// 	showlegend: false,
	// 	marker: {
	// 		size: 15,
	// 		color: ['#22c55e', '#facc15']
	// 	}
	// }
];
export { data, layout };
