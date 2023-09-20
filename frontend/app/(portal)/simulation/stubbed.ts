import { Simulation } from '@/@types/simulation';

export const stubbedSimulation: Simulation = {
	stops: [
		{
			lon: 153.003065,
			lat: -27.494233,
			name: 'St Lucia Stop',
			travel_time: 35
		},
		{
			lon: 153.009596,
			lat: -27.46487,
			name: 'Suncorp Stadium',
			travel_time: 35
		},
		{
			lon: 153.033896,
			lat: -27.455828,
			name: 'Brisbane Airport',
			travel_time: 35
		}
	]
};

export const callAPI = async () => {
	try {
		const res = await fetch('http://127.0.0.1:8000/run_simulation/1/', {method: 'POST',headers: {'Accept': 'application/json','Content-Type': 'application/json', 'Access-Control-Allow-Origin':'*'}, body: `{
      "env_start": 355,
      "time_horizon": 30,
      "itineraries": {
        "0": [{
          "route_id": "412-3136",
          "start": "0",
          "end": "1850"
        }]
      },
      "snapshot_date": "2023-08-01"
    }`});
		const data = await res.json();
		console.log(data);
	} catch (err) {
    console.log(err);
	}
};

