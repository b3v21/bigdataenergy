import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuRadioGroup,
	DropdownMenuRadioItem,
	DropdownMenuSeparator,
	DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import * as React from 'react';
import Plot, { PlotParams } from 'react-plotly.js';
import { config, data, data1, layout, layout1 } from '../../reports';
import Details, { DetailsProps } from './components/details';
import Status from './components/status';
import Routes from './components/routes';

const Sidebar = ({
	simulationSettings,
	setSimulationSettings,
	fetchSimulationData,
	simulationResult
}: DetailsProps) => {
	return (
		<div className="w-[300px]">
			<Tabs defaultValue="details" className="flex flex-col gap-4 h-full">
				<TabsList className="grid grid-cols-3">
					<TabsTrigger value="details">Details</TabsTrigger>
					<TabsTrigger value="routes">Status</TabsTrigger>
					<TabsTrigger value="stops">Routes</TabsTrigger>
				</TabsList>
				<TabsContent value="details" className="flex-1">
					<Details
						simulationSettings={simulationSettings}
						setSimulationSettings={setSimulationSettings}
						fetchSimulationData={fetchSimulationData}
						simulationResult={simulationResult}
					/>
				</TabsContent>
				<TabsContent value="routes" className="flex-1">
					<Status />
				</TabsContent>
				<TabsContent value="stops" className="flex-1">
					<Routes
											simulationSettings={simulationSettings}
											setSimulationSettings={setSimulationSettings}
											fetchSimulationData={fetchSimulationData}
											simulationResult={simulationResult} />
				</TabsContent>
			</Tabs>
		</div>
	);
};


export default Sidebar;
