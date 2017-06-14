$(function() {

  function change_if_all_selected() {
    var xIsChosen = $('#x-selector').val() != '---',
        yIsChosen = $('#y-selector').val() != '---',
        projectIsChosen = $('#r-selector').val() != '---';

    if (xIsChosen && yIsChosen && projectIsChosen) {
      dimension_selector_change();
    }
    return;
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

  $.ajax({
    url: "json"
  }).done(function(data) {
    db_json = data;
    for (var i = 0, len = data.length; i < len; i++) {
      $('#project-selector').append('<option value="'+data[i].id+'">'+data[i].name+'</option>')
      $('#project-selector').prop('disabled', false);
    }
  });

  $('#project-selector').on('change', function() {
    project_id = $(this).find("option:selected").val();

    preserved_x_name = $('#x-selector').find("option:selected").text();
    preserved_y_name = $('#y-selector').find("option:selected").text();

    $('#x-selector').html('<option>---</option>');
    $('#y-selector').html('<option>---</option>');
    
    for (var i = 0, len = db_json.length; i < len; i++) {
      if(db_json[i].id == project_id) {
        project = db_json[i];
        for (var j = 0; j < project.dimensions.length; j++) {
          if('history' in project.dimensions[j].dimension_object) {
            x_selected = (project.dimensions[j].dimension_object.name == preserved_x_name) ? 'selected' : '';
            y_selected = (project.dimensions[j].dimension_object.name == preserved_y_name) ? 'selected' : '';

            $('#x-selector').append('<option '+x_selected+' value="'+project.dimensions[j].id+'">'+project.dimensions[j].dimension_object.name+'</option>');
            $('#x-selector').prop('disabled', false);
            if (project.dimensions[j].dimension_type == 'DecimalDimension') {
              $('#y-selector').append('<option '+y_selected+' value="'+project.dimensions[j].id+'">'+project.dimensions[j].dimension_object.name+'</option>');
              $('#y-selector').prop('disabled', false);
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

});
