'use client';

import Plot from 'react-plotly.js';

import { data, layout } from './plot';
import Sidebar from './components/sidebar';

const Simulation = () => {
	return (
		<div className="flex flex-row gap-8">
			<Sidebar />
			<div className="flex-1">
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
			</div>
		</div>
	);
};

export default Simulation;
