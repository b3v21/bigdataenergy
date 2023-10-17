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
