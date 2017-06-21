$(function(){
  $("#save-path-snap-btn").click(function(){
    project_id = $("#project-selector").find("option:selected").val();
    x_dimension_id = $("#x-selector").find("option:selected").val();
    y_dimension_id = $("#y-selector").find("option:selected").val();

    $("#path-snap-project-id").val(project_id);
    $("#path-snap-x-id").val(x_dimension_id);
    $("#path-snap-y-id").val(y_dimension_id);
  });
});
