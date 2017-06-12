$(function(){
  var djdata = $("#dj-data").data(),
      jsonurl = djdata['url'],
      project = djdata['project'],
      x = djdata['x'],
      y = djdata['y'],
      data = djdata['data'];

  for (var i = 0, len = data.length; i < len; i++) {
    if (data[i].id == project) {
      $("#loading-icon").hide();
      update_path_visualization(
        get_dimension(data[i], x),
        get_dimension(data[i], y)
      );
      break;
    }
  }
});
