// @ts-nocheck
'use client';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ArrowRight } from 'lucide-react';
import dynamic from 'next/dynamic';
import { useMemo } from 'react';
import { PlotParams } from 'react-plotly.js';
import { useTheme } from 'next-themes';

const Report = () => {
	const Plot = useMemo(
		() => dynamic(() => import('react-plotly.js'), { ssr: false }),
		[]
	);

	const theme = useTheme();
	const data1 = {
		values: [300, 120, 131, 12],
		labels: ['Bus', 'Train', 'Metro', 'Other'],
		type: 'pie',
		textinfo: 'label+percent',
		textposition: 'outside',
		automargin: true,
		marker: {
			colors: ['#3b82f6', '#22c55e', '#f97316', '#ef4444']
		}
	};

	const layout1 = {
		margin: {
			b: 0,
			l: 0,
			r: 0,
			t: 0
		},
		font :{
			color: theme.resolvedTheme === 'dark' ? 'white' : '#6b7280'
		},
		plot_bgcolor: theme.resolvedTheme === 'dark' ? '#020817' : 'white',
		paper_bgcolor:theme.resolvedTheme === 'dark' ? '#020817' : 'white'
	};

	var data2 = {
		x: [
			'11:00',
			'11:10',
			'11:20',
			'11:30',
			'11:40',
			'11:50',
			'12:00',
			'12:10',
			'12:20',
			'12:30',
			'12:40',
			'12:50',
			'13:00',
			'13:10',
			'13:20'
		],
		y: [
			0.03, 0.15, 0.08, 0.15, 0.21, 0.25, 0.25, 0.29, 0.31, 0.4, 0.31, 0.2,
			0.12, 0.05
		],
		type: 'scatter',
		hovertemplate:
			'<b>Time: </b>%{x}<br> </br> <b> Percent Delayed Vehicles: </b> %{y}',
		name: 'Delays',
		line: {
			color: '#3b82f6'
		}
	};

	const layout2 = {
		title: {
			text: 'Delayed Vehicle % Over Time',
			font: {
				family: 'Arial',
				size: 14,
				color: theme.resolvedTheme === 'dark' ? 'white' : '#020817'
			},
			xanchor: 'left',
			xref: 'paper',
			x: 0
		},

		autosize: true,
		margin: {
			b: 0,
			l: 35,
			r: 0,
			t: 35
		},
		xaxis: {
			showgrid: false,
			type: 'category',
			zeroline: false,
			showline: false
		},
		yaxis: {
			showgrid: false,
			showline: false,
			zeroline: false,
			tickformat: ',.0%',
			showticklabels: true
		},

		font :{
			color: theme.resolvedTheme === 'dark' ? 'white' : '#6b7280'
		},
		plot_bgcolor: theme.resolvedTheme === 'dark' ? '#020817' : 'white',
		paper_bgcolor:theme.resolvedTheme === 'dark' ? '#020817' : 'white'
	};

	const data3 = {
		values: [316, 141, 10, 25],
		labels: ['Buses', 'Trains', 'Metro', 'Other'],
		type: 'pie',
		textinfo: 'label+percent',
		name: 'CO2',
		hovertemplate:
			'<b> Mode: </b>%{label} %{percent}<br> </br> <b> Emissions: </b>%{value} kg',
		hole: 0.6,
		domain: { column: 0 },
		textposition: 'outside',
		automargin: true,
		marker: {
			colors: ['#3b82f6', '#22c55e', '#f97316', '#ef4444']
		}
	};

	const layout3 = {
		margin: {
			b: 0,
			l: 0,
			r: 0,
			t: 0
		},
		annotations: [
			{
				font: {
					size: 20
				},
				showarrow: false,
				text: '9284kg'
			}
		],
		font :{
			color: theme.resolvedTheme === 'dark' ? 'white' : '#6b7280',
			family: 'Arial',
		},
		plot_bgcolor: theme.resolvedTheme === 'dark' ? '#020817' : 'white',
		paper_bgcolor:theme.resolvedTheme === 'dark' ? '#020817' : 'white'
	};

	var config = { responsive: true };

	var trace1 = {
		x: [10, 12, 18, 21, 23, 29, 31, 44, 55, 59],
		y: ['412', '66', '199', '61', '385', '380', '195', '210', '411', '60'],
		name: 'Low Capacity',
		orientation: 'h',
		marker: {
			color: '#22c55e',
			width: 1
		},
		type: 'bar',
		hovertemplate: '<b>Route: </b>%{y}<br> </br> <b> Percent: </b> %{x}'
	};

	var trace2 = {
		x: [30, 33, 37, 21, 23, 25, 29, 30, 30, 30],
		y: ['412', '66', '199', '61', '385', '380', '195', '210', '411', '60'],
		name: 'Medium Capacity',
		orientation: 'h',
		type: 'bar',
		marker: {
			color: '#f97316',
			width: 1
		},
		hovertemplate: '<b>Route: </b>%{y}<br> </br> <b> Percent: </b> %{x}'
	};

	var trace3 = {
		x: [60, 55, 45, 58, 54, 46, 40, 26, 15, 11],
		y: ['412', '66', '199', '61', '385', '380', '195', '210', '411', '60'],
		name: 'High Capacity',
		orientation: 'h',
		type: 'bar',
		marker: {
			color: '#ef4444',
			width: 1
		},
		hovertemplate: '<b>Route: </b>%{y}<br> </br> <b> Percent: </b> %{x}'
	};

	var data4 = [trace1, trace2, trace3];
	var layout4 = {
		margin: {
			b: 0,
			l: 30,
			r: 0,
			t: 35
		},
		title: {
			text: 'Average Time Route Spent at Capacity',
			font: {
				family: 'Arial',
				size: 14,
				color: theme.resolvedTheme === 'dark' ? 'white' : '#020817'
			},
			xanchor: 'left',
			xref: 'paper',
			x: 0
		},
		barmode: 'stack',
		autosize: true,
		yaxis: {
			type: 'category',
			tickmode: 'linear'
		},
		showlegend: true,
		legend: { orientation: 'h' },
		xaxis: {
			ticksuffix: '%'
		},
		font :{
			color: theme.resolvedTheme === 'dark' ? 'white' : '#6b7280',
			family: 'Arial',
		},
		plot_bgcolor: theme.resolvedTheme === 'dark' ? '#020817' : 'white',
		paper_bgcolor:theme.resolvedTheme === 'dark' ? '#020817' : 'white'

	};

	return (<div >
		<Card className="h-full bg-gray-100/30">
			<CardHeader >
				<CardTitle>Simulation Report</CardTitle>
				<div className = 'flex gap-2'>
				<Badge
					variant="outline"
					className="max-w-fit border-blue-500 bg-blue-500/30 text-blue-500 hover:none"
				>
					ID: SIM001
				</Badge>
				<Badge
					variant="outline"
					className="max-w-fit border-gray-400  text-gray-400 hover:none"
				>
					Date: 15/10/2023 | Run Time: 11:00AM | Duration: 120 mins
				</Badge>
				</div>
			</CardHeader>
			<CardContent>
				<div className="grid grid-cols-3 gap-4">
					<Card className="p-2 gap-4 grid grid-cols-2 justify-between">
						<p className="font-bold cols-span-1"> Fleet </p>
						<div className="col-span-2 flex flex-row font-mono gap-2 items-center text-muted-foreground text-sm">
						<Plot
							data={
								[
									{
										...data1
									}
								] as PlotParams['data']
							}
							layout={layout1}
							config={config}
							style={{ width: "100%", height: "150px" }}
						/>
						<br></br>
						</div>
						<div className="col-span-2 ml-6 mr-6" >
							<Progress value={71} />
						</div>
						<div className="col-span-2 text-right text-xs text-muted-foreground">
							Total Vehicles Active 1000/2000
						</div>
					</Card>

					<Card className="p-2 gap-4 justify-between">
						<p className="font-bold cols-span-1">Route Utilisation</p>
						<br></br>
						<div>
							<Plot
							data={data4}
							layout={layout4}
							config={config}
							style={{ width: "100%", height: "290px"}}
						/>
						<br>
						</br>
						</div>				
					</Card>

					<Card className="p-2 gap-4 justify-between">
						<p className="font-bold cols-span-1">Delays</p>
						<div className="col-span-1 text-right">
							<Badge
								variant="outline"
								className="max-w-fit border-red-500 bg-red-500/30 text-red-500 hover:none"
							>
								<span className="w-2 h-2 rounded-full bg-red-500 mr-2" />
								Significant Delays
							</Badge>
							</div>
						<div>
							<Plot
							data={
								[
									{
										...data2
									}
								] as PlotParams['data']
							}
							layout={layout2}
							config={config}
							style={{ width: "100%", height: "180px" }}
						/>
						<br>
						</br>
						<br></br>
						</div>
							<div className="grid grid-cols-3 gap-1 ">
							<Badge
								variant="secondary"
								className="hover:none"
							>
								<div className="grid grid-cols-1 gap-1 ">
								<p className="text-3xl">
								30.19% 
								</p>
								<p>
								5 min late %
								</p>
								</div>
							</Badge>
							<Badge
								variant="secondary"
								className="hover:none"
							>
								<div className="grid grid-cols-1 gap-1 ">
								<p className="text-3xl">
								22.56% 
								</p>
								<p>
								10 min late %
								</p>
								</div>
							</Badge>
							<Badge
								variant="secondary"
								className="hover:none"
							>
								<div className="grid grid-cols-1 gap-1 ">
								<p className="text-3xl">
								10.21%
								</p>
								<p>
								15 min late %
								</p>
								</div>
							</Badge>
							</div>
					</Card>

					<Card className="p-2 gap-4 justify-between">
						<p className="font-bold cols-span-1">CO2 Emissions</p>
						<div className="col-span-1 text-right">
							<Badge
								variant="outline"
								className="max-w-fit border-orange-500 bg-orange-500/30 text-orange-500 hover:none"
							>
								<span className="w-2 h-2 rounded-full bg-red-500 mr-2" />
								Above Threshold
							</Badge>
							</div>
						<div>
							<Plot
							data={
								[
									{
										...data3
									}
								] as PlotParams['data']
							}
							layout={layout3}
							config={config}
							style={{ width: "100%", height: "180px" }}
						/>
						<br>
						</br>
						</div>			
					</Card>

						<Card className="p-2 gap-4 grid grid-cols-2 justify-between">
							<p className="font-bold cols-span-1"> Passengers </p>
							<div className="col-span-2 flex flex-row font-mono gap-2 items-center text-muted-foreground text-sm">
								<p>Total Passengers</p>
								<ArrowRight size={16} />
								<p> 80,410 </p>
							</div>
							<div className="col-span-2 flex flex-row font-mono gap-2 items-center text-muted-foreground text-sm">
								<p>Total Trips</p>
								<ArrowRight size={16} />
								<p> 120,313 </p>
							</div>
							<div className="col-span-2 flex flex-row font-mono gap-2 items-center text-muted-foreground text-sm">
								<p>Average Trip Time</p>
								<ArrowRight size={16} />
								<p> 32 minutes </p>
							</div>
							<div className="col-span-2 flex flex-row font-mono gap-2 items-center text-muted-foreground text-sm">
								<p>Trips On Time</p>
								<ArrowRight size={16} />
								<p> 83.21% </p>
							</div>
							<div className="col-span-2 flex flex-row font-mono gap-2 items-center text-muted-foreground text-sm">
								<p>Average Trip Distance</p>
								<ArrowRight size={16} />
								<p> 7 km</p>
							</div>
							<br></br>
						</Card>
					</div>
				</CardContent>
			</Card>
		</div>
	);
};

export default Report;
