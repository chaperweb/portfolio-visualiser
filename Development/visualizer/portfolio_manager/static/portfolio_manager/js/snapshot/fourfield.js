$(function(){
  $("#save-fourfield-snap-btn").click(function(){
    x_dimension = $("#x-selector").find("option:selected").text();
    y_dimension = $("#y-selector").find("option:selected").text();
    r_dimension = $("#r-selector").find("option:selected").text();
    start_date = $("#start-date-selector").val();
    end_date = $("#end-date-selector").val();
    zoom = $("#slider-value-selector").find("option:selected").val();

    $("#fourfield-snap-x").val(x_dimension);
    $("#fourfield-snap-y").val(y_dimension);
    $("#fourfield-snap-r").val(r_dimension);
    $("#fourfield-snap-start-date").val(start_date);
    $("#fourfield-snap-end-date").val(end_date);
    $("#fourfield-snap-zoom").val(zoom);
  });
});
