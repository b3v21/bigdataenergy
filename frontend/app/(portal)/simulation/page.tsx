'use client';

import Plot from 'react-plotly.js';

import Sidebar from './components/sidebar';
import { data, layout } from './plot';

const Simulation = () => {
	return (
		<div className="flex flex-row gap-4">
			<Sidebar />
			<div className="flex-1">
				<Plot
					data={data}
					layout={layout}
					config={{
						mapboxAccessToken:
							'pk.eyJ1IjoiamVycnlyeXl5IiwiYSI6ImNsbHAyc3lwNzAxd3ozbHMybmN5MzZwbXcifQ.02Kwsipj1B1BJmk0MYumGA'
					}}
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
