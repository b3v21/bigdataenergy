import { Metadata } from 'next';

import { Button } from '@/components/ui/button';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle
} from '@/components/ui/card';
import { Plus, UploadCloud } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = {
	title: 'Dashboard | Big Data Energy'
};

export default function DashboardPage() {
	return (
		<>
			<div className="flex items-center justify-between space-y-2">
				<h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
			</div>

			<div className="grid gap-4 grid-cols-2">
				<Button asChild variant="outline" className="cursor-pointer">
					<Link href="/simulation" className="min-h-[300px] flex flex-col">
						<CardHeader>
							<CardTitle>New Simulation</CardTitle>
							<CardDescription>
								Run a new simulation with the default settings.
							</CardDescription>
						</CardHeader>
						<CardContent className="grid place-content-center flex-1">
							<Plus size={70} />
						</CardContent>
					</Link>
				</Button>
				<Button asChild variant="outline" className="cursor-pointer">
					<Card className="min-h-[300px] flex flex-col">
						<CardHeader>
							<CardTitle>Import Simulation</CardTitle>
							<CardDescription>
								Import a simulation and its settings
							</CardDescription>
						</CardHeader>
						<CardContent className="grid place-content-center flex-1">
							<UploadCloud size={70} />
						</CardContent>
					</Card>
				</Button>
			</div>
		</>
	);
}
