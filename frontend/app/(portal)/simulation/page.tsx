'use client';

import { useState } from 'react';
import Plot, { PlotParams } from 'react-plotly.js';

import Sidebar from './components/sidebar';
import { data, layout } from './plot';
import HoverCard from './components/hover-card';
import { stubbedSimulation } from './stubbed';
import { Stop } from '@/@types/simulation';

type HoverData = {
	x: number;
	y: number;
	stop: Stop;
};

const HOVER_OFFSET = { x: 10, y: 10 };

const Simulation = () => {
	const { stops } = stubbedSimulation;

	const [hoverData, setHoverData] = useState<HoverData | null>(null);

	return (
		<div className="flex flex-row gap-4">
			<Sidebar />
			<HoverCard data={hoverData} />
			<div className="flex-1">
				<Plot
					data={
						[
							{
								...data,
								lat: stops.map((stop) => stop.lat),
								lon: stops.map((stop) => stop.lon)
							}
						] as PlotParams['data']
					}
					layout={layout}
					config={{
						mapboxAccessToken:
							'pk.eyJ1IjoiamVycnlyeXl5IiwiYSI6ImNsbHAyc3lwNzAxd3ozbHMybmN5MzZwbXcifQ.02Kwsipj1B1BJmk0MYumGA',
						responsive: true
					}}
					style={{
						borderRadius: 'var(--radius)',
						overflow: 'hidden',
						minHeight: '800px'
					}}
					onHover={(event) => {
						const {
							lat,
							lon,
							bbox: { x0, y0 }
						} = event.points[0] as any;

						const stop = stops.find(
							(stop) => stop.lat === lat && stop.lon === lon
						)!;

						setHoverData({
							x: x0 + HOVER_OFFSET.x,
							y: y0 + HOVER_OFFSET.y,
							stop
						});
					}}
					onUnhover={() => setHoverData(null)}
					onClick={(event) => {
						// todo: Focus route tap on sidebar and display more route info
					}}
				/>
			</div>
		</div>
	);
};

export default Simulation;
