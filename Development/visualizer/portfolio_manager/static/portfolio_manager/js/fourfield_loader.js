$(function() {

  $.ajax({
    url: "json"
  }).done(function(data) {
    db_json = data;
    for (var i = 0, len = data.length; i < len; i++) {
      $('#project-selector').append('<option value="'+data[i].id+'">'+data[i].name+'</option>')
    }
  });

  $('#project-selector').on('change', function(){
    project_id = $(this).find("option:selected").val();

    preserved_x_name = $('#x-selector').find("option:selected").text();
    preserved_y_name = $('#y-selector').find("option:selected").text();
    preserved_r_name = $('#r-selector').find("option:selected").text();

    $('#x-selector').html('<option>---</option>');
    $('#y-selector').html('<option>---</option>');
    $('#r-selector').html('<option>---</option>');
    for (var i = 0, len = db_json.length; i < len; i++) {
      if(db_json[i].id == project_id) {
        project = db_json[i];
        for (var j = 0; j < project.dimensions.length; j++) {
          if('history' in project.dimensions[j].dimension_object) {

            x_selected = (project.dimensions[j].dimension_object.name == preserved_x_name) ? 'selected' : '';
            y_selected = (project.dimensions[j].dimension_object.name == preserved_y_name) ? 'selected' : '';
            r_selected = (project.dimensions[j].dimension_object.name == preserved_r_name) ? 'selected' : '';

            if (project.dimensions[j].dimension_type == 'DecimalDimension') {
              $('#x-selector').append('<option '+x_selected+' value="'+project.dimensions[j].id+'">'+project.dimensions[j].dimension_object.name+'</option>');
            }
            if (project.dimensions[j].dimension_type == 'DecimalDimension') {
              $('#y-selector').append('<option '+y_selected+' value="'+project.dimensions[j].id+'">'+project.dimensions[j].dimension_object.name+'</option>');
            }
            if (project.dimensions[j].dimension_type == 'DecimalDimension') {
              $('#r-selector').append('<option '+r_selected+' value="'+project.dimensions[j].id+'">'+project.dimensions[j].dimension_object.name+'</option>');
            }
          }
        }
        break;
      }
    }
    dimension_selector_change();
  });

  $('#x-selector').on('change', dimension_selector_change);
  $('#y-selector').on('change', dimension_selector_change);
  $('#r-selector').on('change', dimension_selector_change);
  $('#start-date-selector').on('change', dimension_selector_change);
  $('#end-date-selector').on('change', dimension_selector_change);

  $('.datepicker').datepicker({'firstDay': 1, 'dateFormat': 'mm/dd/yy'});

});

function dimension_selector_change() {
  x_dimension = $('#x-selector').find("option:selected").text();
  y_dimension = $('#y-selector').find("option:selected").text();
  r_dimension = $('#r-selector').find("option:selected").text();
  start_date = Date.parse($('#start-date-selector').val())/1000;
  end_date = Date.parse($('#end-date-selector').val())/1000;
  $('#visualization').html('');
  fourField(db_json, x_dimension, y_dimension, r_dimension, start_date, end_date);
}  