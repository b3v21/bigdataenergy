export type Itinerary = {
	itinerary_id: number;
	name: string;
	routes: [
		{
			route_id: string;
			start: string;
			end: string;
		}
	];
};

export type Itineraries = Itinerary[];
