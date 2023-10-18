// @ts-nocheck
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
	Command,
	CommandEmpty,
	CommandGroup,
	CommandInput,
	CommandItem
} from '@/components/ui/command';
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog';
import {
	Popover,
	PopoverContent,
	PopoverTrigger
} from '@/components/ui/popover';
import { ChevronsUpDown } from 'lucide-react';
import * as React from 'react';
import { useState } from 'react';
import { PlotParams } from 'react-plotly.js';
import { config } from '../../../reports';
import { DetailsProps } from './details';
import dynamic from 'next/dynamic';

const Routes = ({
	simulationSettings,
	setSimulationSettings,
	fetchSimulationData,
	simulationResult
}: DetailsProps) => {
	const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

	const [suburbSelectorOpen, setSuburbSelectorOpen] = useState(false);
	const [stationSelectorOpen, setStationSelectorOpen] = useState(false);
	const [routeSelectorOpen, setRouteSelectorOpen] = useState(false);
	const [selectedSuburb, setSuburb] = useState();
	const [selectedStation, setStation] = useState();
	const [selectedRoute, setRoute] = useState();
	const resultRoutes = simulationResult ? simulationResult['Routes'] : [];
	const [graphOneStopNames, setGraphOneStopNames] = useState([]);
	const [graphOneStopValues, setGraphOneStopValues] = useState([]);
	const graphOneData = {
		x: graphOneStopNames,
		y: graphOneStopValues,
		type: 'scatter',
		mode: 'lines+markers',
		marker: { color: '#ef4444' },
		hovertemplate:
			'<b>No. Passengers Through Station</b>: %{y}' +
			'<br><b>Time</b>: %{x}<br>'
	};
	const [graphTwoStopNames, setGraphTwoStopNames] = useState([]);
	const [graphTwoStopValues, setGraphTwoStopValues] = useState([]);

	const graphTwoData = {
		x: graphTwoStopNames,
		y: graphTwoStopValues,
		type: 'scatter',
		mode: 'lines+markers',
		marker: { color: '#ef4444' },
		hovertemplate:
			'<i>Station ID</i>: %{x}' +
			'<br><b>Average Passengers at Stop</b>: %{y}<br>'
	};

	{
		/* @ts-ignore  */
	}
	const stationWaitTimes = simulationResult
		? Object.values(simulationResult['Stations']).sort((a, b) => {
				// Assuming "avg_wait" values are numbers, if not, convert as needed
				const avgWaitA = parseFloat(a.avg_wait) || 0;
				const avgWaitB = parseFloat(b.avg_wait) || 0;
				return avgWaitB - avgWaitA;
		  })
		: [];

	const bottleneckValues = stationWaitTimes
		? [
				stationWaitTimes.map((station) => station.stationName),
				stationWaitTimes.map((station) => {
					// Check if "avg_wait" is a valid number before using toFixed
					const avgWait = parseFloat(station.avg_wait);
					return isNaN(avgWait) ? 'N/A' : avgWait.toFixed(2);
				})
		  ]
		: [];
	//var bottleneckValues = simulationResult  ?  [Object.values(simulationResult["Stations"]).filter(station => station["bottleneck"] == true).map(station => station["stationName"]),Object.values(simulationResult["Stations"]).filter(station => station["bottleneck"] == true).map(station => station["avg_wait"]),
	//] : [];

	const graphThreeData = {
		type: 'table',
		header: {
			values: [['<b>Station</b>'], ['<b>Average Wait Time</b>']],
			align: 'center',
			line: { width: 1, color: '#c1c1c1' },
			fill: { color: '#f1f1f1' },
			font: { family: 'Arial', size: 12, color: 'black' }
		},
		cells: {
			values: simulationResult
				? bottleneckValues
				: [['No Data Loaded'], ['No Data Loaded']],
			align: 'center',
			line: { color: '#c1c1c1', width: 1 },
			font: { family: 'Arial', size: 11, color: ['black'] }
		}
	};

	{
		/* @ts-ignore  */
	}
	const handleSetStation = (station) => {
		setStation(station);
		//replot the graph here
		if (
			simulationResult &&
			simulationResult['Stations'] &&
			station &&
			simulationResult['Stations'][station]
		) {
			const peopleChanges =
				simulationResult['Stations'][station]['PeopleChangesOverTime'];
			{
				/* @ts-ignore  */
			}
			setGraphOneStopNames(Object.keys(peopleChanges));
			setGraphOneStopValues(Object.values(peopleChanges));
		} else {
			setGraphOneStopNames([]);
			setGraphOneStopValues([]);
		}
	};
	{
		/* @ts-ignore  */
	}
	const handleSetRoute = (newroute) => {
		const route = newroute.toUpperCase();
		setRoute(route);
		if (route) {
			const stationsArray = Object.values(
				resultRoutes[route.toUpperCase()]['stations']
			);
			{
				/* @ts-ignore  */
			}
			stationsArray.sort((a, b) => a.sequence - b.sequence);
			{
				/* @ts-ignore  */
			}
			const stationNames = stationsArray.map(
				(station) => station.stationName + ` seq: ` + station.sequence
			);
			const stations = [];
			{
				/* @ts-ignore  */
			}
			setGraphTwoStopNames(stationNames);
			for (
				let i = 0;
				i < Object.values(resultRoutes[route]['stations']).length;
				i++
			) {
				stations.push(
					simulationResult['Stations'][
						Object.keys(resultRoutes[route]['stations'])[i]
					]
				);
			}
			{
				/* @ts-ignore  */
			}

			const average_people = stations
				.map((stations) => Object.values(stations['PeopleChangesOverTime']))
				.map(
					(people) =>
						people.reduce((partialSum, a) => partialSum + a, 0) / people.length
				);
			console.log(average_people);
			console.log(stationNames);
			{
				/* @ts-ignore  */
			}
			setGraphTwoStopValues(average_people);
		} else {
			setGraphTwoStopNames([]);
			setGraphTwoStopValues([]);
		}
	};

	return (
		<div className="h-full flex flex-col gap-4 max-h-[725px] overflow-y-scroll">
			<ActionCard title="Station Analysis">
				<Popover
					open={stationSelectorOpen}
					onOpenChange={setStationSelectorOpen}
				>
					<PopoverTrigger asChild>
						<Button
							disabled={!simulationResult}
							variant="outline"
							role="combobox"
							className="w-full justify-between"
						>
							{selectedStation ? selectedStation : 'Select Station...'}
							<ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
						</Button>
					</PopoverTrigger>
					<PopoverContent className="w-full p-0">
						<Command>
							<CommandInput placeholder="Search suburbs..." />
							<CommandEmpty>No stations found.</CommandEmpty>
							<CommandGroup className="max-h-[200px] overflow-y-scroll">
								{(simulationSettings.selectedStations ?? []).map((station) => (
									<CommandItem
										key={station.id}
										onSelect={(currentValue) => {
											handleSetStation(currentValue);
											setStationSelectorOpen(false);
										}}
									>
										{station.id}
									</CommandItem>
								))}
							</CommandGroup>
						</Command>
					</PopoverContent>
				</Popover>
				<Plot
					data={
						[
							{
								...graphOneData
							}
						] as PlotParams['data']
					}
					layout={layout}
					config={config}
				/>
				<Dialog>
					<DialogTrigger asChild>
						<Button variant="outline">Expand</Button>
					</DialogTrigger>
					<DialogContent className="sm:max-w-[800px] h-[800px]">
						<Plot
							data={
								[
									{
										...graphOneData
									}
								] as PlotParams['data']
							}
							layout={layoutFull}
							config={config}
						/>
					</DialogContent>
				</Dialog>
				<div className="font-mono text-sm">
					<b> Average Passenger Waiting Time: </b>{' '}
					{selectedStation
						? (simulationResult['Stations'][selectedStation]?.avg_wait ||
								'N/A') + ' mins'
						: 'N/A'}
				</div>
			</ActionCard>
			<ActionCard title="Route Analysis">
				<Popover open={routeSelectorOpen} onOpenChange={setRouteSelectorOpen}>
					<PopoverTrigger asChild>
						<Button
							disabled={!simulationResult}
							variant="outline"
							role="combobox"
							className="w-full justify-between"
						>
							{selectedRoute ? selectedRoute : 'Select Route...'}
							<ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
						</Button>
					</PopoverTrigger>
					<PopoverContent className="w-full p-0">
						<Command>
							<CommandInput placeholder="Search routes..." />
							<CommandEmpty>No routes found.</CommandEmpty>
							<CommandGroup className="max-h-[200px] overflow-y-scroll">
								{(
									Object.keys(resultRoutes).filter(
										(route) => !route.includes('Walk')
									) ?? []
								).map((route) => (
									<CommandItem
										key={route}
										onSelect={(currentValue) => {
											handleSetRoute(currentValue);
											setRouteSelectorOpen(false);
										}}
									>
										{route}
									</CommandItem>
								))}
							</CommandGroup>
						</Command>
					</PopoverContent>
				</Popover>
				<Plot
					data={
						[
							{
								...graphTwoData
							}
						] as PlotParams['data']
					}
					layout={layoutGraphTwo}
					config={config}
				/>
				<Dialog>
					<DialogTrigger asChild>
						<Button variant="outline">Expand</Button>
					</DialogTrigger>
					<DialogContent className="sm:max-w-[800px] h-[800px]">
						<Plot
							data={
								[
									{
										...graphTwoData
									}
								] as PlotParams['data']
							}
							layout={layoutGraphTwoFull}
							config={config}
						/>
					</DialogContent>
				</Dialog>

				<div className="font-mono text-sm">
					<b> Number of Vehicles Deployed: </b>{' '}
					{selectedRoute
						? Object.keys(
								simulationResult['Routes'][selectedRoute]?.BusesOnRoute || {}
						  ).length
						: 'N/A'}
				</div>
			</ActionCard>

			<ActionCard title="Top Bottle-Necks">
				<Plot
					className="border-radius-15px"
					data={
						[
							{
								...graphThreeData
							}
						] as PlotParams['data']
					}
					layout={layoutGraphThree}
					config={config}
				/>
			</ActionCard>
		</div>
	);
};

const layoutGraphTwo: PlotParams['layout'] = {
	autosize: true,
	height: 250,
	title: {
	  text: '<b>Passenger Volume Per Station<b>',
	  font: {
		  size: 14
		},
	},
	font: {
		family: 'Arial',
		color: 'black'
	},
	margin: {
		l: 25,
		r: 0,
		b: 20,
		t: 40,
		pad: 0
	},
	xaxis: {
		showticklabels: false,
		title: { text: 'Stations', standoff: 240 },
		type: 'category'
	}
};

const layoutGraphTwoFull: PlotParams['layout'] = {
	width: 700,
	height: 700,
	title: {
	  text: '<b>Passenger Volume Per Station<b>',
	  font: {
		  size: 14
		},
	},
	font: {
		family: 'Arial',
		color: 'black'
	},
	margin: {
		l: 25,
		r: 0,
		b: 20,
		t: 40,
		pad: 0
	},
	xaxis: {
		showticklabels: false,
		title: { text: 'Stations', standoff: 700 },
		type: 'category'
	}
};

  const layoutGraphThree: PlotParams['layout'] = {
	autosize: true,
	height: 250,

	font: {
		family: 'Arial',
		color: 'black'
	},
	margin: {
		l: 0,
		r: 0,
		b: 0,
		t: 0,
		pad: 0
	}
};



  const layout: PlotParams['layout'] = {
	autosize: true,
	height: 250,
	title: {
		text: '<b>Passenger Flow Over Time <b>',
		font: {
			size: 14
		}
	},
	font: {
		family: 'Arial',
		color: 'black'
	},
	margin: {
		l: 25,
		r: 0,
		b: 20,
		t: 40,
		pad: 0
	},
	xaxis: {
		showticklabels: false,
		title: { text: 'Time (seconds)', standoff: 240 }
	}
};

const layoutFull: PlotParams['layout'] = {
	width: 700,
	height: 700,
	title: {
		text: '<b>Passenger Flow Over Time <b>',
		font: {
			size: 14
		}
	},
	font: {
		family: 'Arial',
		color: 'black'
	},
	margin: {
		l: 25,
		r: 0,
		b: 20,
		t: 40,
		pad: 0
	},
	xaxis: {
		showticklabels: false,
		title: { text: 'Time (seconds)', standoff: 700 }
	}
};

const ActionCard = ({
	title,
	children
}: {
	title: string;
	children: React.ReactNode;
}) => (
	<Card>
		<CardHeader>
			<CardTitle className="text-xl">{title}</CardTitle>
		</CardHeader>
		<CardContent className="flex flex-col gap-2">{children}</CardContent>
	</Card>
);

export default Routes;
