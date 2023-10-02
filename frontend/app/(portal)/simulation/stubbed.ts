"use client";
// @ts-ignore 
export const callAPIPost = async (stationStates, stationData) => {
	try {

		const format = formatActiveStations(stationStates, stationData)
		const requestBody = {
			env_start: 43200,
			time_horizon: 3600,
			snapshot_date: "2023-10-02",
			active_stations: format,
		  };
		const res = await fetch('http://localhost:8000/itin_check/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(requestBody), // Convert the object to JSON
		});
		const data = await res.json();
		console.log(data);
	} catch (err) {
		console.log(err);
	}
};
// @ts-ignore 
const formatActiveStations = (stationStates, stationData) => {
	const activeStations = [];
  
	for (const stationId in stationStates) {
	  if (stationStates[stationId]) {
		for (const suburb of stationData) {
			// @ts-ignore 
		  const station = suburb.stations.find((s) => s.id === stationId);
		  if (station) {
			activeStations.push({
			  station_id: stationId,
			  lat: station.lat,
			  long: station.long,
			});
			break; // Stop searching for this station in other suburbs
		  }
		}
	  }
	}
  
	return activeStations;
  };