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
function update_path_visualization(project_id, data_id_array) {

  $('#visualization').html('');

  generate_path_svg(generate_path_data(project_id, data_id_array))

  /*
  generate_path_svg(generate_path_data(jQuery.extend(true, {}, project_x_dimension),
                                       jQuery.extend(true, {}, project_y_dimension)));
  */
}

function get_selected_project(project_id) {
  for (var i = 0; i < db_json.length; i++) {
    if(db_json[i].id == project_id) {
      return db_json[i];
    }
  }
  return null;
};

function get_dimension(project, id) {

  for (var j = 0; j < project.dimensions.length; j++) {
      if(project.dimensions[j].id == id) {
        return project.dimensions[j];
      }
  }
  return null;
};

function generate_path_data(project_id, data_id_array) {

  var project = get_selected_project(project_id);
  var pathData = [];
  var y_end_date = 0;

  if (project) {
    for (id in data_id_array) {
      var dimension = get_dimension(project, data_id_array[id]);
      if (dimension) {
        var dataVal = {
          "dimension_name": dimension.dimension_object.name,
          "data": generate_data_chunk(dimension)
        };
        pathData.push(dataVal);
      }
      if (Number(id) === 0) {
        y_end_date = pathData[0].data[pathData[0].data.length - 1].history_date
      } else if (pathData[id].data[pathData[id].data.length - 1].history_date !== y_end_date) {
        pathData[id].data.push(
          {
            "history_date": y_end_date,
            "value": pathData[id].data[pathData[id].data.length - 1].value
          }
        );
      }
    }
  }
  return pathData;
};

// Generates two dimensional set of the data sorted by date
function generate_data_chunk(dimension) {
  data = dimension.dimension_object.history.map(function(val) {
    // Temporal variable to store one single pathData object
    var pathVal = {
      "history_date": "",
      "value": undefined
    };

    pathVal.history_date = Date.parse(val.history_date);
    pathVal.value = val.string;
    return pathVal;
  });

    // Stable sort by date
    data = data.sort(function (a, b) {
      return a.history_date - b.history_date;
    });

    return data;
};

if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
  module.exports = {
    generate_path_data: generate_path_data
  };
}

// Generate the svg container for the visualization
function generate_path_svg(pathData) {
  console.log(pathData)
  // Dimension of the svg box
  // Left and right margin are hardcoded to ensure enough room for axis values
  var height =  Math.max(600, $(window).height() * 0.8),
      width =   Math.max(800, ($(window).width() - 250) * 0.9),
      margin = {
        right: 35,
        left: 65,
        top: height * 0.02,
        bottom: height * 0.05
      };

  var y_data = pathData[0].data
  var x_data = pathData.slice(1)

  // height of the colored x-axis area
  var xAxesHeight = 20;

  // Length of the axis
  var axisLengthX = width - (margin.right + margin.left),
      axisLengthY = height - (margin.top + margin.bottom + (5 * xAxesHeight));

  // human readable timeformat from history_date
  var ddmmyy = d3.timeFormat("%d-%m-%Y");

  //  Parameters for axis transformations
  var pathTransformX = margin.left,
      pathTransformY = margin.top,
      xAxisTransformX = margin.left,
      xAxisTransformY = height - (margin.bottom + (5 * xAxesHeight)),
      timeAxisTransformX = margin.left,
      timeAxisTransformY = height - (margin.bottom + (5 * xAxesHeight)),
      yAxisTransformX = margin.left,
      yAxisTransformY = margin.top;

  // The svg box that everything goes in
  var svg = d3.select("#visualization")
              .append("svg")
              .attr("height", height)
              .attr("width", width)
              .attr("class", "svg-content");

  // The scales of the axis
  var xScale = d3.scaleTime()
            .domain([y_data[0].history_date, y_data[y_data.length - 1].history_date])
            .range([0,axisLengthX]),
      yScale = d3.scaleLinear()
            .domain([0, d3.max(y_data, function(d){return parseFloat(d.value)})])
            .range([axisLengthY,0]);

  var valueLine = d3.line()
                      .curve(d3.curveStepAfter)
                      .x( function(d) { return xScale(d.history_date); } )
                      .y( function(d) { return yScale(d.value); } );

  // The path
  svg.append("path")
      .attr("class", "line")
      .attr("transform", "translate("+pathTransformX+","+pathTransformY+")")
      .attr("height", height)
      .attr("d", valueLine(y_data));

  generate_x_axes(x_data);

  // Time-axis underneath the x-axis
  svg.append("g")
     .attr("transform", "translate("+timeAxisTransformX+","+timeAxisTransformY+")")
     .attr("id", "time-axis")
     .call(d3.axisBottom(xScale)
             .tickFormat(ddmmyy));

  // Y-axis
  svg.append("g")
     .attr("transform", "translate("+yAxisTransformX+","+yAxisTransformY+")")
     .attr("id", "y-axis")
     .call(d3.axisLeft(yScale));

  // Generates the colored x-axes under the graph
  function generate_x_axes(x_data) {

    var axes = x_data
    var rounds = 1

    // colorScale for xAxes
    var xAxesColors = d3.scaleOrdinal()
                        .range([colors[0], colors[1], colors[2]]);

    var amountC = xAxesColors.range().length

    //Append a defs (for definition) element to your SVG
    var defs = svg.append("defs");

    for (round in axes) {
      var axe_label = axes[round].dimension_name
      //Append a linearGradient element to the defs and give it a unique id
      var linearGradient = defs.append("linearGradient")
                                .attr("id", "gradient-"+String(rounds));

      linearGradient.attr("x1", "0%")
                    .attr("y1", "0%")
                    .attr("x2", "100%")
                    .attr("y2", "0%");

      var gradStops = []

      for (color in axes[round].data) {
        if (gradStops.length >= 1) {
          linearGradient.append("stop")
                        .attr("offset", gradStops[(Number(color) - 1)])
                        .attr("stop-color", xAxesColors.range()[Number(color) % amountC]);
        };

        gradStops.push(((axes[round].data[color].history_date - xScale.domain()[0]) /
                        (xScale.domain()[xScale.domain().length - 1] - xScale.domain()[0]))*100 +"%")

        linearGradient.append("stop")
                      .attr("offset", gradStops[Number(color)])
                      .attr("stop-color", xAxesColors.range()[Number(color) % amountC]);

        if (Number(color) === axes[round].data.length-1 && gradStops[gradStops.length-1] != "100%") {
          linearGradient.append("stop")
                        .attr("offset", "100%")
                        .attr("stop-color", xAxesColors.range()[Number(color) % amountC]);
        }
      }

    svg.append("path")
        .data([axes[round].data])
        .attr("fill", "url(#gradient-"+rounds+")")
        .attr("class", "area")
        .attr("transform", "translate("+xAxisTransformX+","+xAxisTransformY+")")
        .attr("id", rounds)
        .attr("d", d3.area().x(function(d) {return xScale(d.history_date)})
                            .y0(function(d) {return rounds * xAxesHeight})
                            .y1(function(d) {return rounds * xAxesHeight + (xAxesHeight - 2)}));
      rounds++;
    }
  }
};
