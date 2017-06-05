$(function(){

  var project = $("#project").data('project'),
      x_dimension = $("#x-dim").data('xdim'),
      y_dimension = $("#y-dim").data('ydim');

  $.ajax({
    url: $("#json-url").data('url')
  }).done(function(data) {
    for (var i = 0, len = data.length; i < len; i++) {
      if (data[i].id == project) {
        update_path_visualization(
          get_dimension(data[i], x_dimension),
          get_dimension(data[i], y_dimension)
        );
        break;
      }
    }
  });

  // console.log(project);
  // console.log(x_dimension);
  // console.log(y_dimension);
});
