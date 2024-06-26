'use client';

import { Itineraries, Stations, Suburbs } from '@/@types';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { useGetSimulationData } from '@/hooks/useGetSimulationData';
import {
	StationStatusColour,
	getItineraryColourFromItinName,
	getStationColourFromWaitTime
} from '@/lib/utils';
import { useTheme } from 'next-themes';
import dynamic from 'next/dynamic';
import { PlotMouseEvent } from 'plotly.js';
import { useEffect, useMemo, useState } from 'react';
import { PlotParams } from 'react-plotly.js';
import HoverCard from './components/hover-card';
import Sidebar from './components/sidebar';
import { layout, routeSettings, stationSettings, walkSettings } from './plot';
import { useSearchParams } from 'next/navigation';
import { stubbedSim } from './stubbedSim';

export type SimulationSettings = {
	date: string;
	startTime: number;
	duration: number;
	selectedSuburbs: Suburbs;
	selectedStations: Stations;
	selectedItineraries: Itineraries;
};

export type HoverData = {
	x: number;
	y: number;
	stationName: string;
	avg_wait: number | null;
	bottleNeck: boolean;
	patronage: { [t: number]: number }[];
};

const HOVER_OFFSET = { x: 10, y: 10 };



/**
 * Renders the simulation page and required components. Holds state for simulation settings. 
 */
const Simulation = () => {
	// Dynamically imports plotly so it doesn't break SSR. Memoized so it doesn't re-import every time state changes
	const Plot = useMemo(
		() => dynamic(() => import('react-plotly.js'), { ssr: false }),
		[]
	);

	// Stores the current tab of the sidebar
	const [sidebarTab, setSidebarTab] = useState('details');
	// Stores information showed on the hover card
	const [hoverData, setHoverData] = useState<HoverData | null>(null);

	// Stores simulation details
	const [simulationSettings, setSimulationSettings] =
		useState<SimulationSettings>({
			date: new Date('July 12, 2023').toISOString().split('T')[0],
			startTime: 355,
			duration: 30,
			selectedSuburbs: [],
			selectedStations: [],
			selectedItineraries: []
		});

	const { toast } = useToast();
	const searchParams = useSearchParams();

	// Retrieves the simulation data
	const {
		data: simulationResult,
		refetch: fetchSimulationData,
		isFetching: simulationDataLoading
	} = useGetSimulationData(
		{
			env_start: simulationSettings.startTime,
			time_horizon: simulationSettings.duration,
			itineraries: simulationSettings.selectedItineraries,
			snapshot_date: simulationSettings.date,
			active_suburbs: simulationSettings.selectedSuburbs.map(
				(suburb) => suburb.suburb
			),
			active_stations: simulationSettings.selectedStations.map(
				(station) => station.id
			)
		},
		{
			enabled: false,
			retry: false,
			onSuccess: (data) => {
				if (
					Object.values(data.Stations).some((station) => {
						if (typeof (station as any).avg_wait !== 'number') return false;
						return (station as any).avg_wait > 10;
					})
				) {
					toast({
						variant: 'default',
						title: '⚠️ High Wait Times',
						description:
							'Some stations have high wait times. Consider adding more services.'
					});
				}
			}
		}
	);

	const theme = useTheme();

	// Memoizes the plot layout so it doesn't flash graph every time state changes
	const plotLayot = useMemo(
		() => ({
			...layout,
			mapbox: {
				...layout.mapbox,
				style: theme.resolvedTheme === 'dark' ? 'dark' : 'light'
			}
		}),
		[theme.resolvedTheme]
	);

	const simulationData = simulationResult as any;

	// Recomputes the stations into a readable format every time simulation data changes
	const itins = useMemo(() => {
		if (!simulationResult) return null;

		return Object.entries(simulationData?.Routes).map((route) => {
			const routeData = (route as any)[1];

			return {
				routeName: (route as any)[0],
				stations: Object.entries(routeData.stations)
					.map((station) => ({
						...(station[1] as any),
						stationName: station[0],
						routeName: (route as any)[0]
					}))
					.sort((a, b) => (a as any).sequence - (b as any).sequence),
				shape: routeData.shape
			};
		});
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [simulationData?.Routes]);

	// Load in stubbed "previous sim" data
	useEffect(() => {
		const loadSim = searchParams.get('loadSim');

		if (!loadSim) return;

		setSimulationSettings(JSON.parse(JSON.stringify(stubbedSim)));

		setTimeout(() => {
			fetchSimulationData();
		}, 1000);
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	const focusStop = (event: Readonly<PlotMouseEvent>) => {};

	return (
		<div className="flex flex-row gap-4 h-full">
			<Sidebar
				currentTab={sidebarTab}
				simLoading={simulationDataLoading}
				setCurrentTab={setSidebarTab}
				simulationSettings={simulationSettings}
				setSimulationSettings={setSimulationSettings}
				fetchSimulationData={fetchSimulationData}
				simulationResult={simulationResult}
				itineraries={itins as any}
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
						!!itins
							? ([
									// routes
									...(itins
										?.filter((itin) => !!itin.shape)
										.map((itin) => ({
											...routeSettings,
											lat: itin.shape.map((coord: any) => coord.lat),
											lon: itin.shape.map((coord: any) => coord.long),
											line: {
												...routeSettings.line,
												color: getItineraryColourFromItinName(itin.routeName)
											}
										})) ?? []),

									// adding walk path if it exists
									...(itins
										?.filter((itin) =>
											(itin.routeName as string).toLowerCase().includes('walk')
										)
										.map((itin) => ({
											...walkSettings,
											lat: itin.stations.map(
												(station) => (station as any).pos.lat
											),
											lon: itin.stations.map(
												(station) => (station as any).pos.long
											)
										})) ?? []),

									// Stations. Rendered last so their z-index is above other plots.
									...(itins?.map((itin) => ({
										...stationSettings,
										lat: itin.stations.map(
											(station) => (station as any).pos.lat
										),
										lon: itin.stations.map(
											(station) => (station as any).pos.long
										),
										marker: {
											...stationSettings.marker,
											color: itin.stations.map((station) => {
												const aw =
													/* @ts-ignore */
													(
														simulationResult?.Stations[
															station.stationName
														] as any
													).avg_wait;
												return typeof aw !== 'number'
													? StationStatusColour.Green
													: getStationColourFromWaitTime(aw as number);
											})
										}
									})) ?? [])
							  ] as PlotParams['data'])
							: ([{ ...routeSettings, lat: [], lon: [] }] as PlotParams['data'])
					}
					layout={plotLayot}
					config={{
						mapboxAccessToken:
							'pk.eyJ1IjoiamVycnlyeXl5IiwiYSI6ImNsbHAyc3lwNzAxd3ozbHMybmN5MzZwbXcifQ.02Kwsipj1B1BJmk0MYumGA',
						responsive: true
					}}
					style={{
						borderRadius: 'var(--radius)',
						overflow: 'hidden',
						height: '100%'
					}}
					onHover={(event) => {
						if (!itins || !simulationResult) return;

						// Excluding routes
						if (event.points[0].curveNumber === 0) return;

						const {
							lat,
							lon,
							bbox: { x0, y0 }
						} = event.points[0] as any;

						const station = Object.values(simulationResult.Stations).find(
							(station) =>
								(station as any).pos.lat === lat &&
								(station as any).pos.long === lon
						);

						if (!station) return;

						setHoverData({
							x: x0 + HOVER_OFFSET.x,
							y: y0 + HOVER_OFFSET.y,
							stationName: (station as any)?.stationName ?? '',
							avg_wait:
								typeof (station as any).avg_wait === 'number'
									? (station as any).avg_wait
									: null,
							bottleNeck: (station as any)?.bottleNeck,
							patronage: (station as any)?.PeopleChangeOverTime
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
