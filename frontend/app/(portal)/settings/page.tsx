'use client';
import { Button } from '@/components/ui/button';
import React, { useState } from 'react';
import { callAPIPost } from '../simulation/stubbed';
import { useGetStationData } from '@/hooks/useGetStationData';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from "@/components/ui/switch"

const Settings = () => {
	const { data, isLoading } = useGetStationData();
	const stationData = data as any;
	const sortedStationData = stationData
	? [...stationData].sort((a, b) => a.suburb.localeCompare(b.suburb))
	: [];

	const [selectedSuburb, setSelectedSuburb] = useState(null);
	const [stationStates, setStationStates] = useState({});

	// @ts-ignore 
	const handleSwitchToggle = (stationId) => {
	const newStationStates = { ...stationStates };
	// @ts-ignore 
	newStationStates[stationId] = !newStationStates[stationId];
	setStationStates(newStationStates);
	};

	// @ts-ignore 
	const handleButtonClick = (suburb) => {
    setSelectedSuburb(suburb);
  };

  return (
    <div className="flex flex-row gap-4">
      <div className="w-[300px]">
        <Card className="h-full">
          <CardHeader>
            <CardTitle>Suburbs</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <p>Loading data...</p>
            ) : (
              <div className="flex flex-col gap-4">
                {sortedStationData.map((suburbData) => (
                  <Card
                    className="p-2 gap-4 grid grid-cols-2 justify-between"
                    key={suburbData.suburb}>
                    <p className="font-bold cols-span-1">{suburbData.suburb}</p>
                    <Button
                      variant="outline"
                      onClick={() => handleButtonClick(suburbData)}
                    >
                      stations: {suburbData.stations.length}
                    </Button>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
      <div className="flex flex-row gap-4"></div>

      {selectedSuburb && (
        <div className="w-[300px]">
          <Card className="h-full">
            <CardHeader>
            	<CardTitle>Stations in {// @ts-ignore  
				selectedSuburb.suburb}</CardTitle>
            </CardHeader>
            <CardContent>
				
              <div className="flex flex-col gap-4">
                {// @ts-ignore 
				selectedSuburb.stations.map((station) => (
                  <Card
                    className="p-2 gap-4 grid grid-cols-2 justify-between"
                    key={station.id}
                  >
                    <p>{station.name} {station.id}</p>
                    <Switch
					// @ts-ignore 
                      checked={stationStates[station.id] || false}
                      onCheckedChange={() => handleSwitchToggle(station.id)}
                    ></Switch>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

	  <Button onClick={() => callAPIPost(stationStates, stationData)}> Generate Itineraries</Button>
    </div>
  );
};

export default Settings;
