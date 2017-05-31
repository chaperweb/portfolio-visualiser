$(function(){
  $("#save-fourfield-snap-btn").click(function(){
    x_dimension_id = $("#x-selector").find("option:selected").val();
    y_dimension_id = $("#y-selector").find("option:selected").val();
    r_dimension_id = $("#r-selector").find("option:selected").val();
    start_date = $("#start-date-selector").val();
    end_date = $("#end-date-selector").val();
    zoom = $("#slider-value-selector").find("option:selected").val();

    $("#fourfield-snap-x-id").val(x_dimension_id);
    $("#fourfield-snap-y-id").val(y_dimension_id);
    $("#fourfield-snap-r-id").val(r_dimension_id);
    $("#fourfield-snap-start-date").val(start_date);
    $("#fourfield-snap-end-date").val(end_date);
    $("#fourfield-snap-zoom").val(zoom);
  });
});
