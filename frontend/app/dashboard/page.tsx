import { Metadata } from 'next';

import { MainNav } from '@/components/main-nav';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export const metadata: Metadata = {
	title: 'Dashboard | Big Data Energy'
};

export default function DashboardPage() {
	return (
		<>
			<div className="flex-col flex">
				<div className="border-b">
					<div className="flex h-16 items-center px-4">
						<MainNav className="mx-6" />
					</div>
				</div>
				<div className="flex-1 space-y-4 p-8 pt-6">
					<div className="flex items-center justify-between space-y-2">
						<h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
					</div>

					<div className="grid gap-4 grid-cols-2">
						<Card>
							<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
								<CardTitle className="text-sm font-medium">
									Total Simulations Run
								</CardTitle>
							</CardHeader>
							<CardContent>
								<div className="text-2xl font-bold">53</div>
								<p className="text-xs text-muted-foreground">
									+20.1% from last month
								</p>
							</CardContent>
						</Card>
						<Card>
							<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
								<CardTitle className="text-sm font-medium">
									Another Stat
								</CardTitle>
							</CardHeader>
							<CardContent>
								<div className="text-2xl font-bold">+2350</div>
								<p className="text-xs text-muted-foreground">
									+180.1% from last month
								</p>
							</CardContent>
						</Card>
					</div>
				</div>
			</div>
		</>
	);
}
