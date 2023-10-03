import type { UseQueryOptions } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import { Simulation } from '@/@types/simulation';
import { simulationKeys } from './queryKeys';
import axios from 'axios';

export type SimulationPayload = {
	env_start: number;
	time_horizon: number;
	itineraries: {
		itinerary_id: number;
		routes: {
			route_id: string;
			start: string;
			end: string;
		}[];
	}[];
	snapshot_date: string;
	active_suburbs: string[];
	active_stations: string[];
};

type QueryOptions = Omit<
	UseQueryOptions<Simulation, unknown, Simulation>,
	'queryKey' | 'queryFn' | 'staleTime'
>;

export function useGetSimulationData(
	payload: SimulationPayload,
	options?: QueryOptions
) {
	return useQuery<Simulation>({
		queryKey: simulationKeys.all,
		queryFn: async () => {
			const { data }: { data: Simulation } = await axios.post(
				'http://localhost:8000/run_simulation/1/',
				payload
			);
			return data;
		},
		staleTime: 1000 * 60 * 60 * 24, // 24 hours
		...options
	});
}
