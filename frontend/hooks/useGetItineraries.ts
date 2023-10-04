import { Itineraries } from '@/@types';
import type { UseQueryOptions } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { itineraryKeys } from './queryKeys';

type Payload = {
	// start time
	env_start: number;
	// duration
	time_horizon: number;
	/* yyyy-mm-dd format */
	snapshot_date: string;
	active_stations: {
		station_id: string;
		lat: number;
		long: number;
	}[];
};

type QueryOptions = Omit<
	UseQueryOptions<Itineraries, unknown, Itineraries>,
	'queryKey' | 'queryFn'
>;

export function useGetItineraries(payload: Payload, options?: QueryOptions) {
	return useQuery<Itineraries>({
		// @ts-ignore
		queryKey: itineraryKeys.all,
		queryFn: async () => {
			const { data }: { data: Itineraries } = await axios.post(
				'http://localhost:8000/itin_check/',
				payload
			);
			return data;
		},
		...options
	});
}
