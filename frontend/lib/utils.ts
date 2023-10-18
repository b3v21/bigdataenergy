import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export enum StationStatusColour {
	Red = '#d2222d,',
	Yellow = '#ffbf00',
	Green = '#22c55e'
}

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

export function getStationColourFromWaitTime(waitTime: number) {
	if (waitTime > 20) {
		return StationStatusColour.Red;
	} else if (waitTime > 10) {
		return StationStatusColour.Yellow;
	} else {
		return StationStatusColour.Green;
	}
}

export function getItineraryColourFromItinName(itinName: string) {
	const possibleColours = [
		'#5D3FD3',
		'#3F00FF',
		'#5D3FD3',
		'#191970',
		'#1F51FF',
		'#4169E1',
		'#0F52BA',
		'#0437F2',
		'#0818A8'
	];

	const getDecimalHashBasedOnItinName = (name: string) => {
		let sum = 0;
		for (let i = 0; i < name.length; i++)
			// @ts-ignore
			sum += ((i + 1) * name.codePointAt(i)) / (1 << 8);
		return sum % 1;
	};

	if (itinName.toLowerCase().includes('walk')) return '#FFA500';

	return possibleColours[
		Math.floor(getDecimalHashBasedOnItinName(itinName) * possibleColours.length)
	];
}
