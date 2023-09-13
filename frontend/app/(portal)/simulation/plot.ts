import { PlotParams } from 'react-plotly.js';

const layout: PlotParams['layout'] = {
	dragmode: 'zoom',
	mapbox: {
		style: 'open-street-map',
		center: { lat: -27.5, lon: 153 },
		zoom: 12
	},
	margin: { r: 0, t: 0, b: 0, l: 0 }
};

const data = {
	name: 'Bus',
	type: 'scattermapbox',
	hoverinfo: 'none',
	mode: 'lines+markers',
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
};

export { data, layout };
