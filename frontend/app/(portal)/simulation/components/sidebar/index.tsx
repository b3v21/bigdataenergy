import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Details, { DetailsProps } from './components/details';
import Routes from './components/routes';
import Status, { ItinProps } from './components/status';

type Props = {
	currentTab: string;
	setCurrentTab: React.Dispatch<React.SetStateAction<string>>;
	simLoading: boolean;
};

const Sidebar = ({
	currentTab,
	setCurrentTab,
	simulationSettings,
	setSimulationSettings,
	fetchSimulationData,
	simulationResult,
	simLoading,
	itineraries
}: DetailsProps & Props & ItinProps) => {
	return (
		<div className="w-[300px]">
			<Tabs
				value={currentTab}
				onValueChange={setCurrentTab}
				className="flex flex-col gap-4 h-full"
			>
				<TabsList className="grid grid-cols-3">
					<TabsTrigger value="details">Details</TabsTrigger>
					<TabsTrigger value="itineraries">Itineraries</TabsTrigger>
					<TabsTrigger value="stops">Graphs</TabsTrigger>
				</TabsList>
				<TabsContent value="details" className="flex-1">
					<Details
						simulationSettings={simulationSettings}
						setSimulationSettings={setSimulationSettings}
						fetchSimulationData={fetchSimulationData}
						simulationResult={simulationResult}
						simLoading={simLoading}
					/>
				</TabsContent>
				<TabsContent value="itineraries" className="flex-1">
					<Status itineraries={itineraries} />
				</TabsContent>
				<TabsContent value="stops" className="flex-1">
					<Routes
						simulationSettings={simulationSettings}
						setSimulationSettings={setSimulationSettings}
						fetchSimulationData={fetchSimulationData}
						simulationResult={simulationResult}
					/>
				</TabsContent>
			</Tabs>
		</div>
	);
};

export default Sidebar;
