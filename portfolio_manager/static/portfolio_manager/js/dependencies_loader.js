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

  function change_if_data_selected() {
    var orgIsChosen = $('#org-selector').val() != '---';
    var typeIsChosen = $('#type-selector').val() != '---';

    if (orgIsChosen && typeIsChosen) {
      selection_changed();
    }
    return;
  }

  function selection_changed() {
    selected_org = $('#org-selector').val();
    selected_type = $('#type-selector').val();
    selected_size = $('#size-selector').val();
    selecter_color = $('#color-selector').val();
    start_date = Date.parse($('#start-date-selector').datepicker( "getDate" ));
    end_date = Date.parse($('#end-date-selector').datepicker( "getDate" ));

    // collect data

    //dependencies(db_json, "visualization", organizations, associationtype, size, color, start_date, end_date);

  };

  $.ajax({
    url: "get_orgs"
  }).done(function(data) {
    $($.parseJSON(data)).map(function () {
      return $('<option>').val(this.id).text(this.name);
    }).appendTo('#org-selector');
    $('#org-selector').append('<option value="kisu">Kissa</option>');

    $('#org-selector').chosen({
        max_selected_options: 5
    });

    $('#org-selector').prop('disabled', false);
  });

  $.ajax({
    url: "json"
  }).done(function(data) {
    db_json = data;
    dependencies(db_json, "visualization");
  });
/*
  $('#org-selector').on('change', function() {
    project_id = $(this).find("option:selected").val();

    preserved_org_array = [];

    $('#org-selector option:selected').each(function () {
      var $this = $(this);
      if ($this.length) {
        var selText = $this.text();
        preserved_org_array.push(selText);
      }
    });

    preserved_size = $('#size-selector').find("option:selected").text();

    $('#org-selector').html('')
    $('#size-selector').html('<option>---</option>');

    for (var i = 0, len = db_json.length; i < len; i++) {
      if(db_json[i].id == project_id) {
        project = db_json[i];
        for (var j = 0; j < project.dimensions.length; j++) {
          if('history' in project.dimensions[j].dimension_object) {
            $('#org-selector').append('<option value="'+project.dimensions[j].id+'">'+project.dimensions[j].dimension_object.name+'</option>');
            $('#org-selector').prop('disabled', false);
            if (project.dimensions[j].dimension_type == 'NumberDimension') {
              $('#size-selector').append('<option value="'+project.dimensions[j].id+'">'+project.dimensions[j].dimension_object.name+'</option>');
              $('#size-selector').prop('disabled', false);
            }
          }
        }
        break;
      }
    }

    var y_id = null;
    $('#size-selector').children().each(function(i, option) {
      if (option.value != '---'
          && (option.text == preserved_y_name || y_id == null))
        y_id = option.value;
    });

    if (y_id != null)
      $('#size-selector').val(y_id);

    if (preserved_org_array !== undefined)
      $('#org-selector').children().each( function(i, option) {
        if (preserved_org_array.some(function(element) {
          return option.text === element
        } )) option.selected = true;
      });



    $('.datepicker').prop('disabled', false);

    change_if_data_selected();
  });
*/
  $('#org-selector').on('change', change_if_data_selected);
  $('#type-selector').on('change', change_if_data_selected);
  $('#size-selector').on('change', change_if_data_selected);
  $('#color-selector').on('change', change_if_data_selected);
  $('.datepicker').on('change', change_if_data_selected);

  $('.datepicker').datepicker({'firstDay': 1, 'dateFormat': 'dd/mm/yy'});

});
