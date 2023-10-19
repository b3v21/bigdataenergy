export const stubbedSim = {
	date: '2023-07-11',
	startTime: 355,
	duration: 30,
	selectedSuburbs: [
		{
			suburb: 'West End',
			stations: [
				{
					id: '1064',
					name: 'Vulture St at West End, stop 7',
					lat: -27.480848,
					long: 153.011631
				},
				{
					id: '1070',
					name: 'Boundary St at Jane Street, stop 6',
					lat: -27.479406,
					long: 153.012279
				},
				{
					id: '1074',
					name: 'Boundary St at West End Junction, stop 5',
					lat: -27.477889,
					long: 153.012562
				},
				{
					id: '1137',
					name: 'Hardgrave Rd at Whynot St, stop 11',
					lat: -27.484226,
					long: 153.006549
				}
			]
		}
	],
	selectedStations: [
		{
			id: '1064',
			name: 'Vulture St at West End, stop 7',
			lat: -27.480848,
			long: 153.011631
		}
	],
	selectedItineraries: [
		{
			itinerary_id: 1,
			routes: [
				{
					route_id: '199-3136',
					start: '1064',
					end: '10802'
				},
				{
					route_id: '385-3136',
					start: '10802',
					end: '817'
				},
				{
					route_id: 'walk',
					start: '817',
					end: '-1'
				}
			],
			name: '199-3136 -> 385-3136 -> walk'
		}
	]
};
