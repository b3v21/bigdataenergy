type Itinerary = {
	[routeId: number]: { Routes: { [routeName: string]: string[] } }[];
};

type Routes = {
	[routeId: string]: {
		PassengerChangesOverTime: {
			[busId: number]: {
				[timestamp: number]: number;
			};
		}[];
		Timeout: {
			[busId: number]: {
				[stopName: string]: number;
			}[];
		};
		stations: {
			[stationId: number]: {
				pos: { lat: number; lon: number };
				stationName: string;
			};
		}[];
	};
};

type Station = {
	[stationId: number]: {
		PeopleChangeOverTime: { [timestamp: number]: number };
		Pos: { lat: number; lon: number };
		stationName: string;
	}[];
};

export type Simulation = {
	Itineraries: Itinerary[];
	Routes: Routes;
	Stations: Station[];
};


type StationData = {
	id: string;
	name: string;
  };
  
export type SuburbResponse = {
	[suburb: string]: {
	stations: StationData[];
	};
  };