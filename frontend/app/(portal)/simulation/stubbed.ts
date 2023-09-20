export const callAPI = async () => {
	try {
		const res = await fetch('http://localhost:8000/run_simulation/1/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: `{
      "env_start": 355,
      "time_horizon": 30,
      "itineraries": {
        "0": {[
          "route_id": "412-3136",
          "start": "0",
          "end": "1850"
        ]}
      },
      "snapshot_date": "2023-08-01"
    }`
		});
		const data = await res.json();
		console.log(data);
	} catch (err) {
		console.log(err);
	}
};
