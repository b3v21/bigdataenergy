import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ArrowRight } from 'lucide-react';

const Status = () => {
	return (
		<Card className="h-full">
			<CardHeader>
				<CardTitle>Status</CardTitle>
			</CardHeader>
			<CardContent>
				<div className="flex flex-col gap-4">
					<Card className="p-2 gap-4 grid grid-cols-2 justify-between">
						<p className="font-bold cols-span-1">Bus 1</p>
						<div className="col-span-1 text-right">
							<Badge
								variant="outline"
								className="max-w-fit border-green-500 bg-green-500/30 text-green-500 hover:none"
							>
								<span className="w-2 h-2 rounded-full bg-green-500 mr-2" />
								Nominal
							</Badge>
						</div>
						<div className="col-span-2 flex flex-row font-mono gap-2 items-center text-muted-foreground text-sm">
							<p>St Lucia</p>
							<ArrowRight size={16} />
							<p>Suncorp</p>
						</div>

						<div className="col-span-2 ">
							<Progress value={71} />
						</div>
						<div className="col-span-2 text-right text-xs text-muted-foreground">
							245/345
						</div>
					</Card>
					<Card className="p-2 gap-4 grid grid-cols-2 justify-between">
						<p className="font-bold cols-span-1">Bus 2</p>
						<div className="col-span-1 text-right">
							<Badge
								variant="outline"
								className="max-w-fit border-red-500 bg-red-500/30 text-red-500 hover:none"
							>
								<span className="w-2 h-2 rounded-full bg-red-500 mr-2" />
								At Capacity
							</Badge>
						</div>
						<div className="col-span-2 flex flex-row font-mono gap-2 items-center text-muted-foreground text-sm">
							<p>F&apos; Val</p>
							<ArrowRight size={16} />
							<p>Suncorp</p>
						</div>

						<div className="col-span-2 ">
							<Progress value={100} className="text-red-500" />
						</div>
						<div className="col-span-2 text-right text-xs text-muted-foreground">
							461/450
						</div>
					</Card>
				</div>
			</CardContent>
		</Card>
	);
};

export default Status;
