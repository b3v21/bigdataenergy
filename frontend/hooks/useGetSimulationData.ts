'use client';

import type { UseQueryOptions } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import { Simulation } from '@/@types/simulation';
import { simulationKeys } from './queryKeys';
import axios from 'axios';

type QueryOptions = Omit<
	UseQueryOptions<Simulation, unknown, Simulation>,
	'queryKey' | 'queryFn' | 'staleTime'
>;

export function useGetSimulationData(options?: QueryOptions) {
	return useQuery<Simulation>({
		queryKey: simulationKeys.all,
		queryFn: async () => {
			const { data }: { data: Simulation } = await axios.post(
				'http://localhost:8000/run_simulation/1/',
				{
					env_start: 355,
					time_horizon: 30,
					itineraries: {
						'0': [{ route_id: '412-3136', start: '0', end: '1850' }]
					},
					snapshot_date: '2023-08-01'
				}
			);
			return data;
		},
		staleTime: 1000 * 60 * 60 * 24, // 24 hours
		...options
	});
}
