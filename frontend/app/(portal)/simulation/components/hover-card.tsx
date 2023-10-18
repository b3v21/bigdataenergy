import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { HoverData } from '../page';

type Props = {
	data: HoverData | null;
};

const HoverCard = ({ data }: Props) => {
	if (!data) return null;

	const { x, y, stationName, avg_wait } = data;
	const warnWaitTime = !!avg_wait && avg_wait > 10;

	return (
		<Card
			className="absolute z-50 p-2 w-[300px] grid gap-y-2"
			style={{
				top: y,
				left: x
			}}
		>
			<p className="font-bold cols-span-1">{stationName}</p>
			<div className="col-span-1 text-right">
				<Badge
					variant="outline"
					className={cn(
						'max-w-fit hover:none',
						warnWaitTime
							? 'border-red-500 bg-red-500/30 text-red-500'
							: 'border-green-500 bg-green-500/30 text-green-500'
					)}
				>
					<span
						className={cn(
							'w-2 h-2 rounded-full mr-2',
							warnWaitTime ? 'bg-red-500' : 'bg-green-500'
						)}
					/>
					{warnWaitTime ? 'High Wait' : 'Nominal'}
				</Badge>
			</div>

			{/* <div className="col-span-2">
				<p className="font-semibold text-sm">Capacity</p>
				<Progress value={71} />
				<div className="text-right text-xs text-muted-foreground">245/345</div>
			</div> */}
			<div className="col-span-2 flex flex-row justify-between">
				<p className="font-semibold text-sm">AVG Wait Time</p>
				<p className="font-mono text-muted-foreground">
					{!!avg_wait ? avg_wait.toFixed(0) : 'N/A'} min
				</p>
			</div>
		</Card>
	);
};

export default HoverCard;
