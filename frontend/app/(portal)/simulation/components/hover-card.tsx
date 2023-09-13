import { Stop } from '@/@types/simulation';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

type Props = {
	data: {
		y: number;
		x: number;
		stop: Stop;
	} | null;
};

const HoverCard = ({ data }: Props) => {
	if (!data) return null;

	const { x, y, stop } = data;

	return (
		<Card
			className="absolute z-50 p-2 w-[300px] grid gap-y-2"
			style={{
				top: y,
				left: x
			}}
		>
			<p className="font-bold cols-span-1">{stop.name}</p>
			<div className="col-span-1 text-right">
				<Badge
					variant="outline"
					className="max-w-fit border-green-500 bg-green-500/30 text-green-500 hover:none"
				>
					<span className="w-2 h-2 rounded-full bg-green-500 mr-2" />
					Nominal
				</Badge>
			</div>

			<div className="col-span-2">
				<p className="font-semibold text-sm">Capacity</p>
				<Progress value={71} />
				<div className="text-right text-xs text-muted-foreground">245/345</div>
			</div>
			<div className="col-span-2 flex flex-row justify-between">
				<p className="font-semibold text-sm">Travel Time</p>
				<p className="font-mono text-muted-foreground">{stop.travel_time}min</p>
			</div>
		</Card>
	);
};

export default HoverCard;
