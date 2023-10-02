'use client';

import type { UseQueryOptions } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import { Simulation, SuburbResponse } from '@/@types/simulation';
import { stationKeys } from './queryKeys';
import axios from 'axios';

type QueryOptions = Omit<
	UseQueryOptions<Simulation, unknown, Simulation>,
	'queryKey' | 'queryFn' | 'staleTime'
>;

export function useGetStationData(options?: QueryOptions) {
	return useQuery<SuburbResponse>({
		// @ts-ignore 
		queryKey: stationKeys.all,
		queryFn: async () => {
			const { data } : { data: SuburbResponse } = await axios.get(
				'http://localhost:8000/station_suburbs'
			);
			return data;
		},
		staleTime: 1000 * 60 * 60 * 24, // 24 hours
		...options
	});
}
