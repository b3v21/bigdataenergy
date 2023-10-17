import { PlotParams } from 'react-plotly.js';

const layout: PlotParams['layout'] = {
	dragmode: 'zoom',
	mapbox: {
		style: 'dark',
		center: { lat: -27.5, lon: 153 },
		zoom: 13
	},
	margin: { r: 0, t: 0, b: 0, l: 0 }
};

const stationSettings = {
	name: 'Stations',
	type: 'scattermapbox',
	hoverinfo: 'none',
	mode: 'markers',
	showlegend: false,
	marker: {
		size: 12,
		color: '#22c55e'
	}
};

const routeSettings = {
	name: 'Routes',
	type: 'scattermapbox',
	showlegend: false,
	hoverinfo: 'none',
	mode: 'markers+lines',
	line: {
		width: 4,
		color: '#4682B4'
	}
};

const walkSettings = {
	name: 'Walks',
	type: 'scattermapbox',
	showlegend: false,
	hoverinfo: 'none',
	mode: 'markers+lines',
	line: {
		width: 4,
		color: '#FFA500',
		dash: 'dot'
	}
};

export { stationSettings, routeSettings, walkSettings, layout };
