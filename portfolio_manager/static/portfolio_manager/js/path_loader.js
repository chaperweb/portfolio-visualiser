/*
Portfolio Visualizer

Copyright (C) 2017 Codento

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
$(function() {

  function change_if_pathdata_selected() {
    var yIsChosen = $('#y-selector').val() != '---',
        projectIsChosen = $('#r-selector').val() != '---';

    if (yIsChosen && projectIsChosen) {
      dimension_selector_change();
    }
    return;
  }

  function dimension_selector_change() {
    x_dimension_id = $('#x-selector').val();
    y_dimension_id = $('#y-selector').val();
    project_id = $('#project-selector').val();
    start_date = Date.parse($('#start-date-selector').datepicker( "getDate" ));
    end_date = Date.parse($('#end-date-selector').datepicker( "getDate" ));

    data_id_array = x_dimension_id

    /* Adding the project id and y-data in the beginning of dataset
    *  Data will be in form of [project_id, y_id, <x1_id...xn_id>]
    */
    data_id_array.unshift(y_dimension_id);
    data_id_array.unshift(project_id);

    generate_path_svg(db_json, "visualization", data_id_array, start_date, end_date);

  };

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
    preserved_x_array = [];
    if($(this).find("option:selected").val() !== "---") {
      $("#save-path-snap-btn").prop("style", "pointer-events:all");
      $("#save-path-snap-btn").removeClass("disabled");
    } else {
      $("#save-path-snap-btn").prop("style", "pointer-events:none");
      $("#save-path-snap-btn").addClass("disabled");
    }
    $('#x-selector option:selected').each(function () {
      var $this = $(this);
      if ($this.length) {
        var selText = $this.text();
        preserved_x_array.push(selText);
      }
    });

    preserved_y_name = $('#y-selector').find("option:selected").text();

    $('#x-selector').html('')
    $('#y-selector').html('<option>---</option>');

    for (var i = 0, len = db_json.length; i < len; i++) {
      if(db_json[i].id == project_id) {
        project = db_json[i];
        for (var j = 0; j < project.dimensions.length; j++) {
          if('history' in project.dimensions[j].dimension_object) {
            $('#x-selector').append('<option value="'+project.dimensions[j].id+'">'+project.dimensions[j].dimension_object.name+'</option>');
            $('#x-selector').prop('disabled', false);
            if (project.dimensions[j].dimension_type == 'NumberDimension') {
              $('#y-selector').append('<option value="'+project.dimensions[j].id+'">'+project.dimensions[j].dimension_object.name+'</option>');
              $('#y-selector').prop('disabled', false);
            }
          }
        }
        break;
      }
    }

    var y_id = null;
    $('#y-selector').children().each(function(i, option) {
      if (option.value != '---'
          && (option.text == preserved_y_name || y_id == null))
        y_id = option.value;
    });

    if (y_id != null)
      $('#y-selector').val(y_id);

    if (preserved_x_array !== undefined)
      $('#x-selector').children().each( function(i, option) {
        if (preserved_x_array.some(function(element) {
          return option.text === element
        } )) option.selected = true;
      });

    $('#x-selector').chosen({
        max_selected_options: 5
    });

    $('.datepicker').prop('disabled', false);

    change_if_pathdata_selected();
  });

  $('#x-selector').on('change', change_if_pathdata_selected);
  $('#y-selector').on('change', change_if_pathdata_selected);
  $('.datepicker').on('change', change_if_pathdata_selected);
  $('.datepicker').datepicker({'firstDay': 1, 'dateFormat': 'dd/mm/yy'});

});
