/*
Portfolio Visualizer

Copyright (C) 2017 Codento

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
var db_json;

// Updates the visualization in case of change in the dropdown
function update_path_visualization(project_x_dimension, project_y_dimension) {

  $('#visualization').html('');

  generate_path_svg(generate_path_data(jQuery.extend(true, {}, project_x_dimension),
                                       jQuery.extend(true, {}, project_y_dimension)));
}

// Generates the data for the visualization
function generate_path_data(x_dimension, y_dimension) {

  // Collect useful values from selected data, convert date to milliseconds
  x_data = x_dimension.dimension_object.history.map(function(val) {
    // Temporal variable to store one single pathData object
    var pathVal = {
      "history_date": "",
      "x": undefined,
      "y": undefined
    };

    pathVal.history_date = Date.parse(val.history_date);
    pathVal.x = val.string;
    return pathVal;
  });

  y_data = y_dimension.dimension_object.history.map(function(val) {
    // Temporal variable to store one single pathData object
    var pathVal = {
      "history_date": "",
      "x": undefined,
      "y": undefined
    };

    pathVal.history_date = Date.parse(val.history_date);
    pathVal.y = val.value;
    return pathVal;
  });

  // Combine data into one array
  data = x_data.concat(y_data);

  // Stable sort by date
  data = data.sort(function (a, b) {
    return a.history_date - b.history_date;
  });

  /* Creates data with no undefined values.

     If there is no new value for x or y it takes previous value,
     in case of change takes the new value.

     If two history_dates are the same, combines values to one element.
     The current and next values are combined to next element, and current element
     is ignored in finalData

     If both are defined leaves that date untouched, occurs when the current element
     is combined one from the last loop.
  */
  var finalData = [];
  for (var i = 0; i < data.length; i++) {
    var current = data[i];
    if (current.x !== undefined && current.y !== undefined) {
      finalData.push(current)
    } else if (i !== data.length - 1 && current.history_date === data[ i + 1 ].history_date) {
      if (data[ i + 1 ].y === undefined) {
        data[ i + 1 ].y = current.y
      } else if (data[ i + 1 ].x === undefined) {
        data[ i + 1 ].x = current.x
      }
    } else if (current.x === undefined) {
      if (i > 0) {
        current.x = data[i-1].x;
      } else {
        current.x = '';
      }
      finalData.push(current)
    } else if (current.y === undefined) {
      if (i > 0) {
        current.y = data[i-1].y;
      } else {
        current.y = 0;
      }
      finalData.push(current)
    }
  };

  // If there is just one value it will be duplicated
  if (finalData.length == 1) {
    finalData[1] = finalData[0];
  }

  return finalData;
}

function get_selected_project() {
  project_id = $('#project-selector').find("option:selected").val();
  for (var i = 0; i < db_json.length; i++) {
    if(db_json[i].id == project_id) {
      return db_json[i];
    }
  }
  return null;
}

function get_dimension(project, id) {
  if (project) {
    for (var j = 0; j < project.dimensions.length; j++) {
        if(project.dimensions[j].id == id) {
          return project.dimensions[j];
        }
    }
  }
  return null;
}

if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
  module.exports = {
    generate_path_data: generate_path_data
  };
}

// Generate the svg container for the visualization
function generate_path_svg(pathData) {
  console.log(pathData)
  // Dimension of the svg box
  // Left margin is hardcoded to ensure enough room for y-axis values
  var height =  Math.max(600, $(window).height() * 0.7),
      width =   Math.max(800, ($(window).width() - 250) * 0.8),
      margin = {
        right: 0,
        left: 60,
        top: height * 0.02,
        bottom: height * 0.05
      };

  // Length of the axis
  var axisLengthX = width * 0.9,
      axisLengthY = height * 0.9;

  // human readable timeformat from history_date
  ddmmyy = d3.timeFormat("%d-%m-%Y");

  //  Parameters for axis transformations
  var pathTransformX = margin.left,
      pathTransformY = margin.top,
      xAxisTransformX = margin.left,
      xAxisTransformY = height - (margin.bottom * 2) + margin.top,
      timeAxisTransformX = margin.left,
      timeAxisTransformY = height - margin.bottom + margin.top,
      yAxisTransformX = margin.left,
      yAxisTransformY = margin.top;

  // The svg box that everything goes in
  var svg = d3.select("#visualization")
              .append("svg")
              .attr("height", height)
              .attr("width", width)
              .attr("class", "svg-content");

  // The scales of the axis
  var x = d3.scaleTime().range([0,axisLengthX]),
      y = d3.scaleLinear().range([axisLengthY,0]);
      z = d3.scaleTime().range([0,axisLengthX]);

  x.domain([pathData[0].history_date, pathData[(pathData.length-1)].history_date]);
  y.domain([0, d3.max(pathData, function(d){return parseFloat(d.y)})]);
  z.domain([pathData[0].history_date, pathData[(pathData.length-1)].history_date]);

  var valueLine = d3.line()
                      .curve(d3.curveStepAfter)
                      .x( function(d) { return x(d.history_date) } )
                      .y( function(d) { return y(d.y) } );

  // The path
  svg.append("path")
      .attr("class", "line")
      .attr("transform", "translate("+pathTransformX+","+pathTransformY+")")
      .attr("height", height)
      .attr("d", valueLine(pathData));

  // X-Axis
  svg.append("g")
     .attr("transform", "translate("+xAxisTransformX+","+xAxisTransformY+")")
     .attr("id", "x-axis")
     .call(d3.axisBottom(x)
     .selectAll("text")
     .data(pathData)
     .text(function(d){return d.x});

  // Time-axis underneath the x-axis
  svg.append("g")
     .attr("transform", "translate("+timeAxisTransformX+","+timeAxisTransformY+")")
     .attr("id", "time-axis")
     .call(d3.axisBottom(z))
     .selectAll("text")
     .data(pathData)
     .text(function(d) { return ddmmyy(Date.parse(d.history_date)) });

  // Y-axis
  svg.append("g")
     .attr("transform", "translate("+yAxisTransformX+","+yAxisTransformY+")")
     .attr("id", "y-axis")
     .call(d3.axisLeft(y));
}
