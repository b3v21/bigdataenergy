import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { getItineraryColourFromItinName } from '@/lib/utils';
import { ArrowDown } from 'lucide-react';

export type ItinProps = {
	itineraries: any[];
};

const Status = ({
	itineraries,
	simulationResult
}: ItinProps & { simulationResult: any }) => {
	return (
		<Card className="h-full relative max-h-full">
			<CardHeader>
				<CardTitle>Itineraries</CardTitle>
			</CardHeader>
			<CardContent className="h-[70vh] max-h-[70vh] overflow-scroll">
				{!itineraries && (
					<div className="inset-0">
						<div className="absolute inset-0 grid place-content-center">
							<p className="font-mono font-bold text-muted-foreground">
								No itineraries 😢
							</p>
						</div>
					</div>
				)}
				<div className="flex flex-col gap-4 ">
					{itineraries?.map((itin) => {
						const endStation =
							itin.stations[itin.stations.length - 1].stationName;

						const itinColour = getItineraryColourFromItinName(itin.routeName);
						return (
							<Card
								key={itin.routeName}
								className="p-2 gap-4 grid grid-cols-2 justify-between"
							>
								<p
									className="font-bold cols-span-1"
									style={{
										color: itinColour
									}}
								>
									{itin.routeName}
								</p>
								<div className="col-span-1 text-right">
									{itin.routeName.toLowerCase().includes('walk') ? (
										<Badge
											variant="outline"
											className="max-w-fit border-blue-500 bg-blue-500/30 text-blue-500 hover:none w-120"
										>
											<span className="w-2 h-2 rounded-full bg-blue-500 mr-2" />
											Walk
										</Badge>
									) : (
										<Badge
											variant="outline"
											className="max-w-fit border-green-500 bg-green-500/30 text-green-500 hover:none w-120"
										>
											<span className="w-2 h-2 rounded-full bg-green-500 mr-2" />
											Bus
										</Badge>
									)}
								</div>
								<div className="col-span-2 flex flex-col font-mono gap-2 items-center text-muted-foreground text-sm">
									<p className="max-w-full whitespace-nowrap overflow-hidden overflow-ellipsis">
										{
											simulationResult.Stations[itin.stations[0].stationName]
												.stationName
										}
									</p>
									<ArrowDown size={16} />
									<p className="max-w-full whitespace-nowrap overflow-hidden overflow-ellipsis">
										{endStation == -1
											? 'Destination 🎯'
											: simulationResult.Stations[endStation].stationName}
									</p>
								</div>

								<div className="col-span-2 ">
									<Progress value={71} />
								</div>
								<div className="col-span-2 text-right text-xs text-muted-foreground">
									245/345
								</div>
							</Card>
						);
					})}
				</div>
			</CardContent>
		</Card>
	);
};

export default Status;
