'use client';

import Plot from 'react-plotly.js';

import { data, layout } from './plot';

const Simulation = () => {
	return (
		<Plot
			data={data}
			layout={layout}
			// config={{
			// 	mapboxAccessToken: process.env.NEXT_PUBLIC_MAPBOX_TOKEN
			// }}
			style={{
				borderRadius: 'var(--radius)',
				overflow: 'hidden',
				minHeight: '800px'
			}}
		/>
	);
};

export default Simulation;
