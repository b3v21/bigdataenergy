import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import * as React from 'react';
import Plot, { PlotParams } from 'react-plotly.js';
import { config, data1, layout1 } from '../../../reports';

import { Button } from '@/components/ui/button';
import { useGetSuburbs } from '@/hooks/useGetSuburbs';

import { useMemo, useState } from 'react';
import {ChevronsUpDown } from 'lucide-react';
import {
	Command,
	CommandEmpty,
	CommandGroup,
	CommandInput,
	CommandItem
} from '@/components/ui/command';

import {
	Popover,
	PopoverContent,
	PopoverTrigger
} from '@/components/ui/popover';

import { DetailsProps } from './details';


const Routes = ({
	simulationSettings,
	setSimulationSettings,
	fetchSimulationData,
	simulationResult
}: DetailsProps) => {
	// const { data: suburbs, isLoading } = useGetSuburbs();

	const [suburbSelectorOpen, setSuburbSelectorOpen] = useState(false);
	const [stationSelectorOpen, setStationSelectorOpen] = useState(false);

	const [routeSelectorOpen, setRouteSelectorOpen] = useState(false);

	const [selectedSuburb, setSuburb] = useState();
	const [selectedStation, setStation] = useState();
	const [selectedRoute, setRoute] = useState();

	//stubbed data to update
	const resultRoutes = ["412", "66-12"];
	//const resultRoutes = Object.keys(simulationResult["Routes"]);

	const [graphOneStopNames, setGraphOneStopNames] = useState([]);
	const [graphOneStopValues, setGraphOneStopValues] = useState([]);
	const graphOneData = {
		x: graphOneStopNames,
		y: graphOneStopValues,
		type: 'scatter',
		mode: 'lines+markers',
		marker: {color: '#ef4444'},
	};

	const [graphTwoStopNames, setGraphTwoStopNames] = useState([]);
	const [graphTwoStopValues, setGraphTwoStopValues] = useState([]);

	const graphTwoData = {
		x: graphTwoStopNames,
		y: graphTwoStopValues,
		type: 'scatter',
		mode: 'lines+markers',
		marker: {color: '#ef4444'},
	};

	//stubbed data update with list of routes etc
	var values = [
		['Chancellors Place Stop D', 'Roma St Staion', 'Coronation Drive Stop 5', 'Coronation Drive Stop 17', 'Chancellors Place Stop D', 'Roma St Staion', 'Coronation Drive Stop 5', 'Coronation Drive Stop 17'],
		[1200000, 20000, 80000, 2000, 1200000, 20000, 80000, 2000],
		[1300000, 20000, 70000, 2000, 1300000, 20000, 70000, 2000]
	]
	const graphThreeData = {
		type: 'table',
		header: {
			values: [["<b>Station</b>"], ["<b>Factor</b>"],
						["<b>Factor</b>"]],
			align: "center",
			line: {width: 1, color: '#c1c1c1'},
			fill: {color: "#f1f1f1"},
			font: {family: "Arial", size: 12, color: "black"}
		},
		cells: {
			values: values,
			align: "center",
			line: {color: "#c1c1c1", width: 1},
			font: {family: "Arial", size: 11, color: ["black"]}
		}
	};

	const stations = useMemo(() => {
		if (!simulationSettings.selectedSuburbs || !selectedSuburb) return [];
		{/* @ts-ignore  */}
		return simulationSettings.selectedSuburbs.filter(x => x.suburb.toLowerCase() == selectedSuburb.toLowerCase())
			.map((suburb) => suburb.stations)
			.flat();
	}, [simulationSettings.selectedSuburbs, selectedSuburb]);

	{/* @ts-ignore  */}
	const handleSetSuburb = (suburb) => {
		setSuburb(suburb);
		handleSetStation(null);
	};

	{/* @ts-ignore  */}
	const handleSetStation = (station) => {
		setStation(station);
		//replot the graph here
		if (simulationResult && simulationResult["Stations"] && station && simulationResult["Stations"][station]){
			const peopleChanges = simulationResult["Stations"][station]["PeopleChangesOverTime"];
								{/* @ts-ignore  */}
			setGraphOneStopNames(Object.keys(peopleChanges));
			setGraphOneStopValues(Object.values(peopleChanges));
		}
		else {
			setGraphOneStopNames([]);
			setGraphOneStopValues([]);
		}
	};
	{/* @ts-ignore  */}
	const handleSetRoute = (route) => {
		setRoute(route);
		// stubbed data to update, here we would update the data by reading the simulation result 
			{/* @ts-ignore  */}
		setGraphTwoStopNames([1, 2]);
			{/* @ts-ignore  */}
		setGraphTwoStopValues([30, 10, 5]);
	}	;

	return (

		<div className="h-full flex flex-col gap-4 max-h-[725px] overflow-y-scroll">
			<ActionCard title ="Station Analysis">
				<Popover open={suburbSelectorOpen} onOpenChange={setSuburbSelectorOpen}>
					<PopoverTrigger asChild>
						<Button
							disabled={!simulationSettings.selectedSuburbs}
							variant="outline"
							role="combobox"
							className="w-full justify-between"
						>{selectedSuburb? selectedSuburb: 'Select Suburb...'}
							<ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
						</Button>
					</PopoverTrigger>
					<PopoverContent className="w-full p-0">
						<Command>
						<CommandInput placeholder="Search suburbs..." />
						<CommandEmpty>No suburbs found.</CommandEmpty>
						<CommandGroup className="max-h-[200px] overflow-y-scroll">
						{(simulationSettings.selectedSuburbs ?? []).map((suburb) => (
							<CommandItem
							key = {suburb.suburb}
							onSelect={(currentValue) => {
								handleSetSuburb(currentValue);
								setSuburbSelectorOpen(false);
							}}>
								{suburb.suburb}

					
							</CommandItem>
						))}
						</CommandGroup>
						</Command>
					</PopoverContent>
				</Popover>
				<Popover
					open={stationSelectorOpen}
					onOpenChange={setStationSelectorOpen}
				>
					<PopoverTrigger asChild>
						<Button
							disabled={!selectedSuburb}
							variant="outline"
							role="combobox"
							className="w-full justify-between"
						>
							{selectedStation? selectedStation: 'Select Station...'}
							<ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
						</Button>
					</PopoverTrigger>
					<PopoverContent className="w-full p-0">
						<Command>
						<CommandInput placeholder="Search suburbs..." />
						<CommandEmpty>No stations found.</CommandEmpty>
						<CommandGroup className="max-h-[200px] overflow-y-scroll">
						{(simulationSettings.selectedSuburbs ?? []).map((suburb) => (
							<CommandItem
							key = {suburb.suburb}
							onSelect={(currentValue) => {
								handleSetSuburb(currentValue);
								setSuburbSelectorOpen(false);
							}}>
								{suburb.suburb}

					
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
			</ActionCard>
			<ActionCard title ="Route Analysis">
				<Popover open={routeSelectorOpen} onOpenChange={setRouteSelectorOpen}>
					<PopoverTrigger asChild>
						<Button
							//disabled={!simulationResult}
							variant="outline"
							role="combobox"
							className="w-full justify-between"
						>{selectedRoute? selectedRoute: 'Select Route...'}
							<ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
						</Button>
					</PopoverTrigger>
					<PopoverContent className="w-full p-0">
						<Command>
						<CommandInput placeholder="Search routes..." />
						<CommandEmpty>No routes found.</CommandEmpty>
						<CommandGroup className="max-h-[200px] overflow-y-scroll">
						{(resultRoutes ?? []).map((route) => (
							<CommandItem
							key = {route}
							onSelect={(currentValue) => {
								handleSetRoute(currentValue);
								setRouteSelectorOpen(false);
							}}>
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
			</ActionCard>

			<ActionCard title ="Top Bottle-Necks">
			<Plot
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
	width: 250,
	height: 250,
	title: {
	  text: '<b>Average Passenger Load Factor<b>',
	  font: {
		  size: 14
		},
	},
	font: {
	  family: 'Arial',
	  color: 'black',
	},
	 margin: {
	  l: 25,
	  r: 0,
	  b: 20,
	  t: 40,
	  pad: 0
	},
	xaxis:{
	  showticklabels: false,
	  title: {text: 'Stations',
	  standoff: 240
	}
	},
	yaxis:{
	  title: {text: 'Capacity (%)',
		},
	},
  };

  const layoutGraphThree: PlotParams['layout'] = {
	width: 250,
	height: 250,

	font: {
		family: 'Arial',
		color: 'black',
	  },
	  margin: {
		l: 0,
		r: 0,
		b: 0,
		t: 0,
		pad: 0
	  }
  }

  const layout: PlotParams['layout'] = {
	width: 250,
	height: 250,
	title: {
	  text: '<b>Passenger Flow Over Time <b>',
	  font: {
		  size: 14
		},
	},
	font: {
	  family: 'Arial',
	  color: 'black',
	},
	 margin: {
	  l: 25,
	  r: 0,
	  b: 20,
	  t: 40,
	  pad: 0
	},
	xaxis:{
	  showticklabels: false,
	  title: {text: 'Time (seconds)',
	  standoff: 240
	}
	},
	yaxis:{
	  title: {text: 'No. Passengers'}
	},
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


export default Routes