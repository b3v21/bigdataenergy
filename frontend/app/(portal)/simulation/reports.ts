import { PlotParams } from 'react-plotly.js';

const layout: PlotParams['layout'] = {
  width: 215,
  height: 250,
  title: {
    text: '<b>Average Passenger Load Factor<b>',
    font: {
        size: 14
      },
  },
  font: {
    family: 'Arial',
    color: 'black',
  },
   margin: {
    l: 25,
    r: 0,
    b: 20,
    t: 40,
    pad: 0
  },
  xaxis:{
    showticklabels: false,
    title: {text: 'Stops',
    standoff: 240
  }
  },
  yaxis:{
    tickformat: '.0%'
  },
};

const data = {
    //fake x and y data
	x: ['Stop1', 'Stop2', 'Stop3', 'Stop4','Stop5', 'Stop6', 'Stop7', 'Stop8','Stop9', 'Stop10', 'Stop11', 'Stop12'],
	y: [0.1, 0.15, 0.20, 0.43, 0.63, 0.65, 0.65, 0.7, 0.81, 0.81, 0.6, 0.3, 0.45],
	type: 'scatter',
	mode: 'lines+markers',
	marker: {color: 'blue'},
};



  //fake data

  const layout1: PlotParams['layout'] = {
    title: {
        text: '<b>Stops at Capcity<b>',
        font: {
            size: 14
          },
      },
    barmode: 'stack',
    xaxis: {
      title: {text: 'Stops',
    }
    },
    yaxis: {
        ticks: 'inside',
        type: 'category' 
      },
    width: 215,
    height: 250,
    font: {
      family: 'Arial',
      color: 'black',
    },
     margin: {
      l: 25,
      r: 0,
      b: 20,
      t: 40,
      pad: 0
    },
    showlegend: false
  };

  const trace1 = {
    x: [30, 10, 20],
    y: ['412', '420', '380'],
    type: 'bar',
    name: 'Low Capacity',
    orientation: 'h', // horizontal orientation
    marker: {
      color: '#22c55e',
      width: 1,
    },
  };
  
  const trace2 = {
    x: [20, 30, 10],
    y: ['412', '420', '380'],
    type: 'bar',
    name: 'Medium Capacity',
    orientation: 'h', // horizontal orientation
    marker: {
      color: 'orange',
      width: 1,
    },
  };
  
  const trace3 = {
    x: [10, 20, 30],
    y: ['412', '420', '380'],
    type: 'bar',
    name: 'High Capacity',
    orientation: 'h', // horizontal orientation
    marker: {
      color: '#ef4444',
      width: 1,
    },
  };
  
  const data1 = [trace1, trace2, trace3] as PlotParams['data'];


export {data, layout, data1, layout1 };
