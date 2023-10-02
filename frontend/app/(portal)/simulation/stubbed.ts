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
					"active_stations": "[1, 10, 1797]"	
    			}`
		});
		const data = await res.json();
		console.log(data);
	} catch (err) {
		console.log(err);
	}
};
