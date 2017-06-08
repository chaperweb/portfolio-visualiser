$(function(){
  var djdata = $("#dj-data").data(),
      x = djdata['x'],
      y = djdata['y'],
      r = djdata['r'],
      start = Date.parse(djdata['start'])/1000,
      end = Date.parse(djdata['end'])/1000,
      zoom = djdata['zoom'],
      data = djdata['data'];

  $("#loading-icon").hide();
  fourField(data, x, y, r, start, end, zoom);
});
