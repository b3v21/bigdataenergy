import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

const Sidebar = () => {
	return (
		<Card>
			<CardHeader>
				<CardTitle>Simulation Settings</CardTitle>
				<Input name="population" />
			</CardHeader>
		</Card>
	);
};

export default Sidebar;
