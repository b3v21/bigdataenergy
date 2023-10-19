import { Button } from '@/components/ui/button';
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow
} from '@/components/ui/table';
import { Delete, ExternalLink, Import } from 'lucide-react';
import Link from 'next/link';

const stubbedSimulations = [
	{
		id: 'SIM001',
		dateRan: '2021-10-01',
		duration: '1h 30m'
	},
	{
		id: 'SIM002',
		dateRan: '2021-10-02',
		duration: '1h 30m'
	},
	{
		id: 'SIM003',
		dateRan: '2021-10-03',
		duration: '2h 00m'
	}
];

export function SimulationsTable() {
	return (
		<div>
			<p className="text-xl font-bold">Previous Simulations</p>
			<Table>
				<TableHeader>
					<TableRow>
						<TableHead className="w-[100px]">ID</TableHead>
						<TableHead className="w-full">Date Ran</TableHead>
						<TableHead>Duration</TableHead>
						<TableHead>Actions</TableHead>
					</TableRow>
				</TableHeader>
				<TableBody>
					{stubbedSimulations.map((simulation) => (
						<TableRow key={simulation.id}>
							<TableCell className="font-medium">{simulation.id}</TableCell>
							<TableCell>{simulation.dateRan}</TableCell>
							<TableCell>{simulation.duration}</TableCell>
							<TableCell
								align="right"
								className="flex flex-row gap-2 items-center"
							>
								<Link passHref href="/simulation?loadSim=1">
									<Button size="icon" className="gap-2">
										<ExternalLink />
									</Button>
								</Link>
								<Button size="icon" variant="destructive" className="gap-2">
									<Delete />
								</Button>
							</TableCell>
						</TableRow>
					))}
				</TableBody>
			</Table>
		</div>
	);
}
