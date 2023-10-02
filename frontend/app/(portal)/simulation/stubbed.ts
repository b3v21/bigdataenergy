"use client";
export const callAPIPost = async () => {
	try {
		const res = await fetch('http://localhost:8000/itin_check/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: `{
					"env_start": 43200,
					"time_horizon": 3600,
					"snapshot_date": "2023-10-02",
					"active_stations": [
						{
							"station_id" : "1",
							"lat" : -27.467834,
							"long" : 153.019079
						},
						{
							"station_id" : "10",
							"lat" : -27.468003,
							"long" : 153.02397
						},
						{
							"station_id" : "1797",
							"lat" : -27.497974,
							"long" : 153.01113

						}
					]
    			}`
		});
		const data = await res.json();
		console.log(data);
	} catch (err) {
		console.log(err);
	}
};
