export type FullStation = {
	station_id: string;
	station_code: string;
	name: string;
	lat: number;
	long: number;
	location_type: number;
	suburb: string;
};

export type Station = {
	id: string;
	lat: number;
	long: number;
	name: string;
};

export type Stations = Station[];
