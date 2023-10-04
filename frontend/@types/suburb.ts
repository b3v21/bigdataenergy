import { Stations } from './station';

export type Suburb = {
	suburb: string;
	stations: Stations;
};

export type Suburbs = Suburb[];
