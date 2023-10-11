'use client';

import { useGetSimulationData } from '@/hooks/useGetSimulationData';
import { useMemo, useState } from 'react';
import Plot, { PlotParams } from 'react-plotly.js';
import HoverCard from './components/hover-card';
import Sidebar from './components/sidebar';
import { layout, data as plotData } from './plot';
import { Itineraries, Stations, Suburbs } from '@/@types';
import { Card } from '@/components/ui/card';
import { PlotMouseEvent } from 'plotly.js';

export type SimulationSettings = {
	date: string;
	startTime: number;
	duration: number;
	selectedSuburbs: Suburbs;
	selectedStations: Stations;
	selectedItineraries: Itineraries;
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
			date: new Date().toISOString().split('T')[0],
			startTime: 355,
			duration: 30,
			selectedSuburbs: [],
			selectedStations: [],
			selectedItineraries: [
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
			]
		});
	const [sidebarTab, setSidebarTab] = useState('details');

	// Retrieves the simulation data
	const { data: simulationResult, refetch: fetchSimulationData } =
		useGetSimulationData(
			{
				env_start: simulationSettings.startTime,
				time_horizon: simulationSettings.duration,
				itineraries: simulationSettings.selectedItineraries,
				snapshot_date: '2023-08-01',
				active_suburbs: simulationSettings.selectedSuburbs.map(
					// default st lucia
					(suburb) => suburb.suburb
				),
				active_stations: simulationSettings.selectedStations.map(
					// default 1815
					(station) => station.id
				)
			},
			{
				enabled: false
			}
		);

	// todo: remove any types once data typed correctly
	const simulationData = simulationResult as any;

	// Recomputes the stations into a readable format every time simulation data changes
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

	const focusStop = (event: Readonly<PlotMouseEvent>) => {};

	return (
		<div className="flex flex-row gap-4">
			<Sidebar
				currentTab={sidebarTab}
				setCurrentTab={setSidebarTab}
				simulationSettings={simulationSettings}
				setSimulationSettings={setSimulationSettings}
				fetchSimulationData={fetchSimulationData}
				simulationResult={simulationResult}
			/>
			<HoverCard data={hoverData} />
			<div className="flex-1 relative">
				{!simulationData && (
					<div className="absolute z-50 inset-0 flex items-center justify-center rounded-md ">
						<Card className="flex flex-col items-center gap-4 p-4 bg-transparent backdrop-blur-sm border-slate-600">
							<p className="text-2xl font-bold">No simulation data</p>
							<p className="text-xl">Please select suburbs and stations</p>
						</Card>
					</div>
				)}

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
					onClick={focusStop}
				/>
			</div>
		</div>
	);
};

export default Simulation;
