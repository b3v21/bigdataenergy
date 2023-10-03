'use client';

import { useGetSimulationData } from '@/hooks/useGetSimulationData';
import { useMemo, useState } from 'react';
import Plot, { PlotParams } from 'react-plotly.js';
import HoverCard from './components/hover-card';
import Sidebar from './components/sidebar';
import { layout, data as plotData } from './plot';
import { Stations, Suburbs } from '@/@types';

export type SimulationSettings = {
	selectedSuburbs: Suburbs;
	selectedStations: Stations;
};

type HoverData = {
	x: number;
	y: number;
	stopName: string;
};

const HOVER_OFFSET = { x: 10, y: 10 };

const Simulation = () => {
	// Stores information showed on the hover card
	const [hoverData, setHoverData] = useState<HoverData | null>(null);
	// Stores simulation details
	const [simulationSettings, setSimulationSettings] =
		useState<SimulationSettings>({
			selectedSuburbs: [],
			selectedStations: []
		});

	// Retrieves the simulation data
	const {
		data: simulationResult,
		isLoading,
		refetch: fetchSimulationData
	} = useGetSimulationData(
		{
			env_start: 355,
			time_horizon: 30,
			itineraries: [
				{
					itinerary_id: 0,
					routes: [
						{
							route_id: '412-3136',
							start: '0',
							end: '1850'
						}
					]
				}
			],
			snapshot_date: '2023-08-01',
			active_suburbs: ['St Lucia'],
			active_stations: ['1815']
		},
		{
			enabled: false
		}
	);

	// todo: remove any types once data typed correctly
	const simulationData = simulationResult as any;

	// The following recomputes the stations into a readable format every time simulation data changes
	const routeStations = useMemo(() => {
		if (!simulationResult) return null;

		return (
			// Formatting data for plotly
			Object.entries(simulationData?.Routes)
				.map((route) =>
					Object.entries((route as any)[1].stations).map(
						(station) => station[1]
					)
				)[0]
				// todo: remove any types once data typed correctly
				.sort((a, b) => (a as any).sequence - (b as any).sequence)
		);
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [simulationData?.Routes]);

	return (
		<div className="flex flex-row gap-4">
			<Sidebar
				simulationSettings={simulationSettings}
				setSimulationSettings={setSimulationSettings}
				fetchSimulationData={fetchSimulationData}
			/>
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
