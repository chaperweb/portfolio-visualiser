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

function generate_path_data(data_id_array) {

  var project = get_selected_project(data_id_array[0]);
  var pathData = [];
  var y_end_date = 0;

  data_id_array = data_id_array.slice(1)

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
      /*takes the last date from the first data set
      * the date is used to ensure that the last value
      * of the x-data is properly shown on the coloured axis
      * in case that the last update of the said value has been
      * before the last update of the y-value.
      */
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

// Generate the svg container for the visualization
function generate_path_svg(target, data_id_array) {

  $('#'+ target).html('');

  // Dimension of the svg box
  // Left and right margin are hardcoded to ensure enough room for axis values
  var height =  Math.max(600, $(window).height() * 0.8),
      width =   Math.max(800, ($(window).width() - 250) * 0.9),
      margin = {
        right: 35,
        left: 85,
        top: height * 0.02,
        bottom: height * 0.05
      };

  var pathData = generate_path_data(data_id_array)
  var y_data = pathData[0].data
  var x_data = pathData.slice(1)

  // height of the colored x-axis area and maximum amount of x-axis
  var xAxesHeight = 20;
  var xAxesMaxOptions = 5;

  // Length of the axis
  var axisLengthX = width - (margin.right + margin.left),
      axisLengthY = height - (margin.top + margin.bottom + (xAxesMaxOptions * xAxesHeight));

  // human readable timeformat from history_date
  var ddmmyy = d3.timeFormat("%d-%m-%Y");

  //  Parameters for axis transformations
  var pathTransformX = margin.left,
      pathTransformY = margin.top,
      xAxisTransformX = margin.left,
      xAxisTransformY = height - (margin.bottom + (xAxesMaxOptions * xAxesHeight)),
      timeAxisTransformX = margin.left,
      timeAxisTransformY = height - (margin.bottom + (xAxesMaxOptions * xAxesHeight)),
      yAxisTransformX = margin.left,
      yAxisTransformY = margin.top;

  // The svg box that everything goes in
  var svg = d3.select("#"+ target)
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

  // Y-axis label
  svg.append("text")
     .attr("id", "yAxisLabel")
     .attr("transform", "translate("+(pathTransformX + 10) +","+(pathTransformY + margin.top) +")")
     .text(pathData[0].dimension_name)


   // div element for the x-axis values
   var div = d3.select("#"+target).append("div")
         .style("position", "fixed")
         .style("background", "white")
         .style("pointer-events", "none")
         .style("opacity", 0);

   // Variable to hold previous divValueId and bisector for x-values
   var divValueId = Infinity;
   var bisectX = d3.bisector(function(d) { return d.history_date; }).right;

   // Updates the div element value and relocates it when needed.
   function updateDiv(data, element) {
     var currentId = bisectX(data, Date.parse(xScale.invert(d3.event.offsetX)))
     if (currentId != divValueId || div.text() != data[currentId - 1]) {
       divValueId = currentId
       div.style("opacity", .7);
       div.html(data[divValueId - 1].value)
           .style("left", element.getScreenCTM().e + xScale(data[divValueId - 1].history_date) + "px")
           .style("top", element.getScreenCTM().f + element.getBBox().y + "px");
     }
   }

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
      /* Coloring the linearGradient, the color appears as blocks because
      *  the color change locations are with identical offset
      *
      *  for the dataset of length = 1 the last point is added.
      */
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

    // Add the x-axis label
    var xLabel = svg.append("text")
                     .attr("class", "pathXlabel")
                     .attr("transform", "translate("+ 0 +","+xAxisTransformY+")")
                     .attr("y", ((rounds * xAxesHeight) + (xAxesHeight - 2)))
                     .attr("x", 0)
                     .text(axes[round].dimension_name)
                     .on("mouseover", function(){ xHoverLabel.style("opacity", 1)};)
                     .on("mouseout", function(){ xHoverLabel.style("opacity", 0);});;

    // Add the coloured area
    svg.append("path")
        .data([axes[round].data])
        .attr("fill", "url(#gradient-"+rounds+")")
        .attr("class", "area")
        .attr("transform", "translate("+xAxisTransformX+","+xAxisTransformY+")")
        .attr("id", rounds)
        .attr("d", d3.area().x(function(d) {return xScale(d.history_date)})
                            .y0(function(d) {return rounds * xAxesHeight + 2})
                            .y1(function(d) {return rounds * xAxesHeight + xAxesHeight - 1}))
        .on("mousemove", function(d){ updateDiv(d, this)};)
        .on("mouseout", function(){return div.style("opacity", 0);});


    var xHoverLabel = svg.append("text")
                         .attr("class", "pathXlabel")
                         .attr("transform", "translate("+ 0 +","+xAxisTransformY+")")
                         .attr("y", ((rounds * xAxesHeight) + (xAxesHeight - 2)))
                         .attr("x", 0)
                         .text(axes[round].dimension_name)
                         .style("pointer-events", "none")
                         .style("opacity", 0);

    /*
    * If the label doesn't fit to left margin the overflowing text will be faded
    */
    var textWidth = xLabel.node().getBBox().width;

    if (textWidth > (margin.left - 5)) {

      linearGradient = defs.append("linearGradient")
                            .attr("id", "textGradient-"+String(rounds));

      linearGradient.attr("x1", "0%")
                    .attr("y1", "0%")
                    .attr("x2", "100%")
                    .attr("y2", "0%");

      linearGradient.selectAll("stop")
                    .data([
                      {offset: "0%", color: "#000000"},
                      {offset: (((margin.left - 20 )/ textWidth) * 100) + "%", color: "#000000"},
                      {offset: (((margin.left - 5) / textWidth) * 100) + "%", color: "#ffffff"},
                      {offset: "100%", color: "#ffffff"}
                      ])
                    .enter().append("stop")
                    .attr("offset", function(d) { return d.offset; })
                    .attr("stop-color", function(d) { return d.color; });

      xLabel.attr("fill", "url(#textGradient-"+rounds+")")
    };

      rounds++;
    }
  }
};
