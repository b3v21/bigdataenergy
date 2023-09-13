export type Simulation = {
	stops: Stop[];
};

export type Stop = {
	lon: number;
	lat: number;
	name: string;
	travel_time: number;
};
