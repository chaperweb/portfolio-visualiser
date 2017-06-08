var db_json;

function update_path_visualization(project_x_dimension, project_y_dimension) {

  $('#visualization').html('');

  generate_path_svg(generate_path_data(jQuery.extend(true, {}, project_x_dimension),
                                       jQuery.extend(true, {}, project_y_dimension)));
}

function generate_path_data(x_dimension, y_dimension) {

  x_data = x_dimension.dimension_object.history.map(function(val) {
    val.x = val.string;
    return val;
  });

  y_data = y_dimension.dimension_object.history.map(function(val) {
    val.y = val.value;
    return val;
  });

  data = x_data.concat(y_data);
  for (var i = 0; i < data.length; i++) {
    data[i].idx = i;
  }

  // Stable sort
  data = data.sort(function (a, b) {
    diff = Date.parse(a.history_date) - Date.parse(b.history_date);
    if (diff != 0) {
      return diff;
    }
    return a.idx - b.idx;
  });

  for (var i = 0; i < data.length; i++) {
    if('y' in data[i]) {
      if(i > 0) {
        data[i].x = data[i-1].x;
      }
      else {
        data[i].x = '';
      }
    }
  }

  for (var i = 0; i < data.length; i++) {
    if(! ('y' in data[i])) {
      if(i > 0) {
        data[i].y = data[i-1].y;
      }
      else {
        data[i].y = 0;
      }
    }
  }

  // Remove duplicates
  data = data.filter(function(val, index, array) {
    if(index < array.length - 1 && val.history_date == array[index+1].history_date) {
      return false;
    }
    return true;
  });

  if (data.length == 1) {
    data[1] = data[0];
  }

  return data.map(function(val) {
    parts = val.history_date.split('T');
    val.date = parts[0]
    return val;
  });

}

function generate_path_svg(pathData) {
  // Dimension of the svg box
  var height = Math.max(600, $(window).height()*0.7),
      width = Math.max(700, ($(window).width()-250)*0.8),
      margin = {
        right: 0,
        left: width*0.05,
        top: height*0.02,
        bottom: height*0.05
      };

  // Length of the axis
  var axisLengthX = width*0.9,
      axisLengthY = height * 0.9;

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
  var x = d3.scaleLinear().range([0,axisLengthX]),
      y = d3.scaleLinear().range([axisLengthY,0]);
      z = d3.scaleLinear().range([0,axisLengthX]);

  x.domain([0, (pathData.length-1)]);
  y.domain([0, d3.max(pathData, function(d){return parseFloat(d.y)})]);
  z.domain([0, (pathData.length-1)]);

  var valueLine = d3.line()
                      .curve(d3.curveStepAfter)
                      .x(function(d,i){return x(i)})
                      .y(function(d){return y(d.y)});

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
     .call(d3.axisBottom(x).ticks(pathData.length-1))
     .selectAll("text")
     .data(pathData)
     .text(function(d){return d.x});

  // Time-axis underneath the x-axis
  svg.append("g")
     .attr("transform", "translate("+timeAxisTransformX+","+timeAxisTransformY+")")
     .attr("id", "time-axis")
     .call(d3.axisBottom(z).ticks(pathData.length-1))
     .selectAll("text")
     .data(pathData)
     .text(function(d){return d.date});

  // Y-axis
  svg.append("g")
     .attr("transform", "translate("+yAxisTransformX+","+yAxisTransformY+")")
     .attr("id", "y-axis")
     .call(d3.axisLeft(y));
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

function dimension_selector_change() {
  x_dimension_id = $('#x-selector').find("option:selected").val();
  y_dimension_id = $('#y-selector').find("option:selected").val();

  selected_project = get_selected_project();

  update_path_visualization(
    get_dimension(selected_project, x_dimension_id),
    get_dimension(selected_project, y_dimension_id)
  );
}

if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
  module.exports = {
    generate_path_data: generate_path_data
  };
}
