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
	
	const [selectedSuburb, setSuburb] = useState();
	const [selectedStation, setStation] = useState();

	const [graphOneStopNames, setGraphOneStopNames] = useState([]);
	const [graphOneStopValues, setGraphOneStopValues] = useState([]);
	const graphOneData = {
		x: graphOneStopNames,
		y: graphOneStopValues,
		type: 'scatter',
		mode: 'lines+markers',
		marker: {color: 'blue'},
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

	return (

		<div className="h-full flex flex-col gap-4">
			<ActionCard title ="Station Data">
				<Popover open={suburbSelectorOpen} onOpenChange={setSuburbSelectorOpen}>
					<PopoverTrigger asChild>
						<Button
							disabled={!simulationSettings.selectedSuburbs}
							variant="outline"
							role="combobox"
							className="w-full justify-between"
						>{selectedSuburb? selectedSuburb: 'Select suburb...'}
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
							{(simulationSettings.selectedStations ?? []).map((station) => (
								<CommandItem
								key = {station.id}
								onSelect={(currentValue) => {
									handleSetStation(currentValue);
									setStationSelectorOpen(false);
								}}
								>
									{station.id}
								</CommandItem>
							))

							}
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
		</div>
	);
};


const layout: PlotParams['layout'] = {
	width: 215,
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
	  title: {text: 'No. Passengers',
		standoff: 200}
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