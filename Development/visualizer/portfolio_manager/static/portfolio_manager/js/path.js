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
  var height = 400,
      width = 700,
      marginY = 200,
      marginX = 100;
      timeY = height+50

  // debugger;
  // pathData = [{"date": "01-05-16", "y": 150.10, "x": "Teuvo"},
  //                  {"date": "15-05-16", "y": 170.10, "x": "Teppo"},
  //                  {"date": "01-06-16", "y": 50.03, "x": "Matti"},
  //                  {"date": "01-07-16", "y": 200.04, "x": "Teppo"}];

  //debugger;

  var svg = d3.select("#visualization")
              .append("svg")
              .attr("height", height+marginY)
              .attr("width", width+marginX)
              .attr("class", "svg-content")
              .append("g")
              .attr("transform", "translate("+50+","+50+")");

  var parseTime = d3.timeParse("%d-%m-%y");

  var x = d3.scaleLinear().range([0,width]),
      y = d3.scaleLinear().range([height,0]);
      z = d3.scaleLinear().range([0,width]);

  x.domain([0, (pathData.length-1)]);
  y.domain([0, d3.max(pathData, function(d){return parseFloat(d.y)})]);
  z.domain([0, (pathData.length-1)]);

  var valueLine = d3.line()
                      .curve(d3.curveStepAfter)
                      .x(function(d,i){return x(i)})
                      .y(function(d){return y(d.y)});

  svg.append("path")
      .attr("class", "line")
      .attr("d", valueLine(pathData));

  svg.append("g")
     .attr("transform", "translate(0,"+height+")")
     .call(d3.axisBottom(x).ticks(pathData.length-1))
     .selectAll("text")
     .data(pathData)
     .text(function(d){return d.x});

  svg.append("g")
     .call(d3.axisLeft(y));

  svg.append("g")
    .attr("transform", "translate(0,"+timeY+")")
    .call(d3.axisBottom(z).ticks(pathData.length-1))
    .selectAll("text")
    .data(pathData)
    .text(function(d){return d.date});
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
