import { useMemo, useState } from 'react';
import { Check, ChevronsUpDown } from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
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

import { cn } from '@/lib/utils';
import { useGetSuburbs } from '@/hooks/useGetSuburbs';
import { SimulationSettings } from '../../../page';

export type DetailsProps = {
	simulationSettings: SimulationSettings;
	setSimulationSettings: React.Dispatch<
		React.SetStateAction<SimulationSettings>
	>;
	fetchSimulationData: VoidFunction;
};

const Details = ({
	simulationSettings: { selectedSuburbs, selectedStations },
	setSimulationSettings,
	fetchSimulationData
}: DetailsProps) => {
	const [suburbSelectorOpen, setSuburbSelectorOpen] = useState(false);
	const [stationSelectorOpen, setStationSelectorOpen] = useState(false);

	const { data: suburbs, isLoading } = useGetSuburbs();

	const stations = useMemo(() => {
		if (!suburbs || !selectedSuburbs.length) return [];

		return selectedSuburbs.map((suburb) => suburb.stations).flat();
	}, [suburbs, selectedSuburbs]);

	const handleRunSimulation = () => {
		fetchSimulationData();
	};

	return (
		<Card className="h-full">
			<CardHeader>
				<CardTitle>Simulation Details</CardTitle>
			</CardHeader>
			<CardContent className="flex flex-col gap-4">
				<Popover open={suburbSelectorOpen} onOpenChange={setSuburbSelectorOpen}>
					<PopoverTrigger asChild>
						<Button
							disabled={isLoading}
							variant="outline"
							role="combobox"
							className="w-full justify-between"
						>
							{selectedSuburbs.length
								? selectedSuburbs.map((suburb) => suburb.suburb).join(', ')
								: 'Select suburb...'}
							<ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
						</Button>
					</PopoverTrigger>
					<PopoverContent className="w-full p-0">
						<Command>
							<CommandInput placeholder="Search suburbs..." />
							<CommandEmpty>No suburbs found.</CommandEmpty>
							<CommandGroup className="max-h-[200px] overflow-y-scroll">
								{(suburbs ?? []).map((suburb) => (
									<CommandItem
										key={suburb.suburb}
										onSelect={(currentValue) => {
											setSimulationSettings({
												selectedSuburbs: selectedSuburbs.includes(suburb)
													? selectedSuburbs.filter(
															(suburb) =>
																suburb.suburb.toLowerCase() !== currentValue
													  )
													: [
															...selectedSuburbs,
															suburbs!.find(
																(suburb) =>
																	suburb.suburb.toLowerCase() === currentValue
															)!
													  ],
												selectedStations: []
											});
											setSuburbSelectorOpen(false);
										}}
									>
										<Check
											className={cn(
												'mr-2 h-4 w-4',
												selectedSuburbs.includes(suburb)
													? 'opacity-100'
													: 'opacity-0'
											)}
										/>
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
							disabled={!selectedSuburbs.length}
							variant="outline"
							role="combobox"
							className="w-full justify-between"
						>
							{selectedStations.length
								? selectedStations.map((station) => station.id).join(', ')
								: 'Select stations...'}
							<ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
						</Button>
					</PopoverTrigger>
					<PopoverContent className="w-full p-0">
						<Command>
							<CommandInput placeholder="Search suburbs..." />
							<CommandEmpty>No stations found.</CommandEmpty>
							<CommandGroup className="max-h-[200px] overflow-y-scroll">
								{(stations ?? []).map((station) => (
									<CommandItem
										key={station.id}
										onSelect={(currentValue) => {
											setSimulationSettings({
												selectedSuburbs,
												selectedStations: selectedStations.includes(station)
													? selectedStations.filter(
															(station) => station.id !== currentValue
													  )
													: [
															...selectedStations,
															stations!.find(
																(station) => station.id === currentValue
															)!
													  ]
											});
											setStationSelectorOpen(false);
										}}
									>
										<Check
											className={cn(
												'mr-2 h-4 w-4',
												selectedStations.includes(station)
													? 'opacity-100'
													: 'opacity-0'
											)}
										/>
										{station.id}
									</CommandItem>
								))}
							</CommandGroup>
						</Command>
					</PopoverContent>
				</Popover>
				<Button
					className="w-full"
					disabled={!selectedStations.length}
					onClick={handleRunSimulation}
				>
					run simulation
				</Button>
			</CardContent>
		</Card>
	);
};

export default Details;
