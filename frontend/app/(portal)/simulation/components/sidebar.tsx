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
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import * as React from 'react';
import Plot, { PlotParams } from 'react-plotly.js';
import { config, data, data1, layout, layout1 } from '../reports';
import Status from './sidebar/components/status';

const Sidebar = () => {
	return (
		<div className="w-[300px]">
			<Tabs defaultValue="routes" className="flex flex-col gap-4 h-full">
				<TabsList className="grid grid-cols-3">
					<TabsTrigger value="routes">Status</TabsTrigger>
					<TabsTrigger value="details">Details</TabsTrigger>
					<TabsTrigger value="stops">Routes</TabsTrigger>
				</TabsList>
				<TabsContent value="routes" className="flex-1">
					<Status />
				</TabsContent>
				<TabsContent value="details" className="flex-1">
					<Details />
				</TabsContent>
				<TabsContent value="stops" className="flex-1">
					<Routes />
				</TabsContent>
			</Tabs>
		</div>
	);
};

const Details = () => (
	<Card className="h-full">
		<CardHeader>
			<CardTitle>Details</CardTitle>
			<Input name="population" defaultValue="" />
		</CardHeader>
	</Card>
);
const Routes = () => {
	//to do: move css styling
	//to do: connect to api call
	const options = [
		'412',
		'411',
		'66',
		'199',
		'418',
		'199',
		'188',
		'182',
		'33',
		'61',
		'385',
		'70',
		'410',
		'419',
		'380',
		'375',
		'370',
		'300',
		'62',
		'170',
		'111',
		'444',
		'550',
		'500'
	];
	const [position, setPosition] = React.useState(options[0]);
	const dropdownContainerStyle = {
		maxHeight: '400px',
		overflowY: 'auto',
		overflowX: 'hidden'
	};

	const handleOptionSelect = (selectedOption: React.SetStateAction<string>) => {
		//replot the graph

		// Update the state with the selected option
		setPosition(selectedOption);
	};

	return (
		<Card className="h-full">
			<CardHeader>
				<CardTitle>Routes</CardTitle>
			</CardHeader>
			<CardContent>
				<div className="flex flex-col gap-4">
					<DropdownMenu>
						<DropdownMenuTrigger asChild>
							<Button variant="outline">Selected: {position} </Button>
						</DropdownMenuTrigger>
						<DropdownMenuContent>
							{/* @ts-ignore */}
							<div style={dropdownContainerStyle}>
								<DropdownMenuSeparator />
								<DropdownMenuRadioGroup
									value={position}
									onValueChange={handleOptionSelect}
								>
									{options.map((option) => (
										<DropdownMenuRadioItem key={option} value={option}>
											{option}
										</DropdownMenuRadioItem>
									))}
								</DropdownMenuRadioGroup>
							</div>
						</DropdownMenuContent>
					</DropdownMenu>
					<Card className="p-2 gap-4 grid grid-cols-2 justify-between">
						{/* @ts-ignore */}
						<Plot
							data={
								[
									{
										...data
									}
								] as PlotParams['data']
							}
							layout={layout}
							config={config}
						/>
					</Card>
					<Card className="p-2 gap-4 grid grid-cols-2 justify-between">
						{/* @ts-ignore */}
						<Plot data={data1} layout={layout1} config={config} />
					</Card>
				</div>
			</CardContent>
		</Card>
	);
};

export default Sidebar;
