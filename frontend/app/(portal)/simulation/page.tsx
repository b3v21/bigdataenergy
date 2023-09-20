'use client';

import { Simulation as SimulationData } from '@/@types/simulation';
import { useGetSimulationData } from '@/hooks/useGetSimulationData';
import Sidebar from './components/sidebar';
import { useMemo, useState } from 'react';
import Plot, { PlotParams } from 'react-plotly.js';
import { layout, data as plotData } from './plot';
import HoverCard from './components/hover-card';

type HoverData = {
	x: number;
	y: number;
	stopName: string;
};

const HOVER_OFFSET = { x: 10, y: 10 };

const Simulation = () => {
	const [hoverData, setHoverData] = useState<HoverData | null>(null);
	const { data, isLoading } = useGetSimulationData();

	// Todo: remove once data typed correctly
	const simulationData = data as any;

	const routeStations = useMemo(() => {
		if (!data) return null;

		return Object.entries(simulationData?.Routes).map((route) =>
			Object.entries((route as any)[1].stations).map((station) => station[1])
		)[0];
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [simulationData?.Routes]);

	return (
		<div className="flex flex-row gap-4">
			<Sidebar />
			<HoverCard data={hoverData} />
			<div className="flex-1">
				{/* @ts-ignore  */}
				<Plot
					data={
						[
							{
								...plotData,
								lat: routeStations?.map((station) => (station as any).pos.lat),
								lon: routeStations?.map((station) => (station as any).pos.long)
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
						if (!routeStations) return;

						console.log('hover', routeStations);

						const {
							lat,
							lon,
							bbox: { x0, y0 }
						} = event.points[0] as any;

						const stop = routeStations.find(
							(station) =>
								(station as any).pos.lat === lat &&
								(station as any).pos.long === lon
						)!;

						setHoverData({
							x: x0 + HOVER_OFFSET.x,
							y: y0 + HOVER_OFFSET.y,
							stopName: (stop as any).stationName
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
