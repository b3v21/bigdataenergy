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

type Data = {
	itineraries: Itineraries;
};

type QueryOptions = Omit<
	UseQueryOptions<Data, unknown, Data>,
	'queryKey' | 'queryFn'
>;

export function useGetItineraries(payload: Payload, options?: QueryOptions) {
	return useQuery<Data>({
		queryKey: itineraryKeys.all,
		queryFn: async () => {
			const { data }: { data: Data } = await axios.post(
				'http://localhost:8000/itin_check/',
				payload
			);
			return data;
		},
		...options
	});
}
