import { Check, ChevronsUpDown, Loader2 } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useGetItineraries } from '@/hooks/useGetItineraries';
import { useGetSuburbs } from '@/hooks/useGetSuburbs';
import { cn } from '@/lib/utils';
import { SimulationSettings } from '../../../page';

type Props = {
	simLoading: boolean;
};

export type DetailsProps = {
	simulationSettings: SimulationSettings;
	setSimulationSettings: React.Dispatch<
		React.SetStateAction<SimulationSettings>
	>;
	fetchSimulationData: VoidFunction;
	simulationResult: any;
};

/**
 * Renders the details section of the sidebar.
 */
const Details = ({
	simulationSettings,
	setSimulationSettings,
	fetchSimulationData,
	simulationResult,
	simLoading
}: DetailsProps & Props) => {
	// State
	const [suburbSelectorOpen, setSuburbSelectorOpen] = useState(false);
	const [stationSelectorOpen, setStationSelectorOpen] = useState(false);
	const [itinerarySelectorOpen, setItinerarySelectorOpen] = useState(false);

	// Getter for suburbs data
	const { data: suburbs, isLoading } = useGetSuburbs();

	// Getter for itin data
	const {
		data: retData,
		isLoading: itinerariesLoading,
		refetch: refetchItineraries
	} = useGetItineraries(
		{
			env_start: 355,
			time_horizon: 120,
			snapshot_date: simulationSettings.date,
			active_stations: simulationSettings.selectedStations.map(
				({ lat, long, id }) => ({
					station_id: id,
					lat,
					long
				})
			)
		},
		{
			enabled: !!simulationSettings.selectedStations.length,
			retry: false
		}
	);

	// Get all stations from selected suburbs. Memoized.
	const stations = useMemo(() => {
		if (!suburbs || !simulationSettings.selectedSuburbs.length) return [];

		return simulationSettings.selectedSuburbs
			.map((suburb) => suburb.stations)
			.flat();
	}, [suburbs, simulationSettings.selectedSuburbs]);

	useEffect(() => {
		if (simulationSettings.selectedStations.length > 1) {
			refetchItineraries();
		}
	}, [refetchItineraries, simulationSettings.selectedStations]);

	// Starts the simulation by activating the simulation getter.
	const handleRunSimulation = () => {
		fetchSimulationData();
	};

	return (
		<div className="h-full flex flex-col gap-4">
			<ActionCard title="Active Start Stations">
				<Popover open={suburbSelectorOpen} onOpenChange={setSuburbSelectorOpen}>
					<PopoverTrigger asChild>
						<Button
							disabled={isLoading}
							variant="outline"
							role="combobox"
							className="w-full justify-between"
						>
							<span className="max-w-full whitespace-nowrap overflow-ellipsis overflow-hidden">
								{simulationSettings.selectedSuburbs.length
									? simulationSettings.selectedSuburbs
											.map((suburb) => suburb.suburb)
											.join(', ')
									: 'Select suburb...'}
							</span>
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
												...simulationSettings,
												selectedSuburbs:
													simulationSettings.selectedSuburbs.includes(suburb)
														? simulationSettings.selectedSuburbs.filter(
																(suburb) =>
																	suburb.suburb.toLowerCase() !== currentValue
														  )
														: [
																...simulationSettings.selectedSuburbs,
																suburbs!.find(
																	(suburb) =>
																		suburb.suburb.toLowerCase() === currentValue
																)!
														  ],
												selectedStations: []
											});
										}}
									>
										<Check
											className={cn(
												'mr-2 h-4 w-4',
												simulationSettings.selectedSuburbs.includes(suburb)
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
							disabled={!simulationSettings.selectedSuburbs.length}
							variant="outline"
							role="combobox"
							className="w-full justify-between"
						>
							<span className="max-w-full whitespace-nowrap overflow-ellipsis overflow-hidden">
								{simulationSettings.selectedStations.length
									? simulationSettings.selectedStations
											.map((station) => station.name)
											.join(', ')
									: 'Select stations...'}
							</span>

							<ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
						</Button>
					</PopoverTrigger>
					<PopoverContent className="w-full p-0">
						<Command>
							<CommandInput placeholder="Search suburbs..." />
							<CommandEmpty>No stations found.</CommandEmpty>
							<CommandGroup className="max-h-[200px] overflow-y-scroll">
								{(stations ?? []).map((currStation) => (
									<CommandItem
										key={currStation.id}
										onSelect={() => {
											setSimulationSettings({
												...simulationSettings,
												selectedStations:
													simulationSettings.selectedStations.includes(
														currStation
													)
														? simulationSettings.selectedStations.filter(
																(station) => station.id !== currStation.id
														  )
														: [
																...simulationSettings.selectedStations,
																stations!.find(
																	(station) => station.id === currStation.id
																)!
														  ]
											});
										}}
									>
										<Check
											className={cn(
												'mr-2 h-4 w-4',
												simulationSettings.selectedStations.includes(
													currStation
												)
													? 'opacity-100'
													: 'opacity-0'
											)}
										/>
										{currStation.name}
									</CommandItem>
								))}
							</CommandGroup>
						</Command>
					</PopoverContent>
				</Popover>
			</ActionCard>

			<ActionCard title="Timing Details">
				<div>
					<Label htmlFor="email">Date</Label>
					<Input
						type="date"
						name="date"
						id="date"
						placeholder="Simulation Date"
						disabled // todo: enable
						value={simulationSettings.date}
					/>
				</div>
				<div>
					<Label htmlFor="start-time">Start (mins from midnight)</Label>
					<Input
						type="number"
						name="start-time"
						id="start-time"
						placeholder="Start Time"
						value={simulationSettings.startTime}
						onChange={(e) =>
							setSimulationSettings({
								...simulationSettings,
								startTime: Number(e.target.value)
							})
						}
					/>
				</div>
				<div>
					<Label htmlFor="duration">Duration</Label>
					<Input
						type="number"
						name="duration"
						id="duration"
						placeholder="Duration"
						value={simulationSettings.duration}
						onChange={(e) =>
							setSimulationSettings({
								...simulationSettings,
								duration: Number(e.target.value)
							})
						}
					/>
				</div>
			</ActionCard>

			<Popover
				open={itinerarySelectorOpen}
				onOpenChange={setItinerarySelectorOpen}
			>
				<PopoverTrigger asChild>
					<Button
						disabled={
							!simulationSettings.selectedStations.length || itinerariesLoading
						}
						variant="outline"
						role="combobox"
						className="w-full justify-between"
					>
						<span className="max-w-full whitespace-nowrap overflow-ellipsis overflow-hidden">
							{simulationSettings.selectedItineraries.length
								? simulationSettings.selectedItineraries
										.map((itinerary) => itinerary.name)
										.join(', ')
								: 'Select itineraries...'}
						</span>
						<ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
					</Button>
				</PopoverTrigger>
				<PopoverContent className="w-full p-0">
					<Command>
						<CommandInput placeholder="Search itineraries..." />
						<CommandEmpty>No itineraries found.</CommandEmpty>
						<CommandGroup className="max-h-[200px] overflow-y-scroll">
							{(retData?.itineraries ?? []).map((currentItin) => (
								<CommandItem
									key={currentItin.itinerary_id}
									onSelect={() => {
										setSimulationSettings({
											...simulationSettings,
											selectedItineraries:
												simulationSettings.selectedItineraries.includes(
													currentItin
												)
													? simulationSettings.selectedItineraries.filter(
															(itinerary) =>
																itinerary.itinerary_id !==
																currentItin.itinerary_id
													  )
													: [
															...simulationSettings.selectedItineraries,
															retData?.itineraries!.find(
																(itinerary) =>
																	itinerary.itinerary_id ===
																	currentItin.itinerary_id
															)!
													  ]
										});
										setStationSelectorOpen(false);
									}}
								>
									<Check
										className={cn(
											'mr-2 h-4 w-4',
											simulationSettings.selectedItineraries.includes(
												currentItin
											)
												? 'opacity-100'
												: 'opacity-0'
										)}
									/>
									<span className="font-bold text-muted-foreground mr-2">
										{currentItin.itinerary_id}
									</span>{' '}
									{currentItin.name}
								</CommandItem>
							))}
						</CommandGroup>
					</Command>
				</PopoverContent>
			</Popover>
			<Button
				className="w-full capitalize"
				disabled={!simulationSettings.selectedStations.length || simLoading}
				onClick={handleRunSimulation}
			>
				{simLoading ? (
					<Loader2 size={16} className="animate-spin" />
				) : (
					'run simulation'
				)}
			</Button>
		</div>
	);
};

/**
 * Renders a card with a title and applied styling.
 */

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

export default Details;
