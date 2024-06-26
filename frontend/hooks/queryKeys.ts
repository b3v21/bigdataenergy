export const simulationKeys = {
	all: ['simulation'],
	// todo: Change this to include params once they're set up
	byId: (id: number) => [...simulationKeys.all, id]
};
export const suburbKeys = {
	all: ['suburbs']
};
export const stationKeys = {
	all: ['stations']
};

export const itineraryKeys = {
	all: ['itineraries']
};