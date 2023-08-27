import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

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
				<TabsContent value="details">
					<Details />
				</TabsContent>
				<TabsContent value="stops">
					<Routes />
				</TabsContent>
			</Tabs>
		</div>
	);
};

const Status = () => (
	<Card className="h-full">
		<CardHeader>
			<CardTitle>Status</CardTitle>
			<Input name="population" defaultValue="" />
		</CardHeader>
	</Card>
);

const Details = () => (
	<Card className="h-full">
		<CardHeader>
			<CardTitle>Details</CardTitle>
			<Input name="population" defaultValue="" />
		</CardHeader>
	</Card>
);
const Routes = () => (
	<Card className="h-full">
		<CardHeader>
			<CardTitle>Routes</CardTitle>
			<Input name="population" defaultValue="" />
		</CardHeader>
	</Card>
);

export default Sidebar;
