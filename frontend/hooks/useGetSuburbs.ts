import { Suburbs } from '@/@types/suburb';
import type { UseQueryOptions } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { suburbKeys } from './queryKeys';

type QueryOptions = Omit<
	UseQueryOptions<Suburbs, unknown, Suburbs>,
	'queryKey' | 'queryFn' | 'staleTime'
>;

export function useGetSuburbs(options?: QueryOptions) {
	return useQuery<Suburbs>({
		queryKey: suburbKeys.all,
		queryFn: async () => {
			const { data }: { data: Suburbs } = await axios.get(
				'http://localhost:8000/station_suburbs'
			);
			return data;
		},
		...options,
		staleTime: 1000 * 60 * 60 * 24 * 1 // 1 days
	});
}
