$(function(){
  $.ajax({
    url: $("#dj-data").data('url')
  }).done(function(data) {
      var x = $("#dj-data").data('x'),
          y = $("#dj-data").data('y'),
          r = $("#dj-data").data('r'),
          start = Date.parse($("#dj-data").data('start'))/1000,
          end = Date.parse($("#dj-data").data('end'))/1000,
          zoom = $("#dj-data").data('zoom');
          console.log("HI");
      fourField(data, x, y, r, start, end, zoom);
  });
});
