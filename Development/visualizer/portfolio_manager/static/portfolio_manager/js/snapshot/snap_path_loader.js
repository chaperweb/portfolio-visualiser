$(function(){
  var x_dimension = $("#x-dim").data('xdim'),
      y_dimension = $("#y-dim").data('ydim');

  console.log(x_dimension);
  console.log(y_dimension);
  update_path_visualization(x_dimension, y_dimension);
});
