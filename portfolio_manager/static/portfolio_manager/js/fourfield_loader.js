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

  function change_if_all_selected() {
    var xIsChosen = $('#x-selector').val() != '---',
        yIsChosen = $('#y-selector').val() != '---',
        rIsChosen = $('#r-selector').val() != '---';

    if (xIsChosen && yIsChosen && rIsChosen) {
      dimension_selector_change();
    }
    return;
  }

  function dimension_selector_change() {
    x_dimension = $('#x-selector').find("option:selected").text();
    y_dimension = $('#y-selector').find("option:selected").text();
    r_dimension = $('#r-selector').find("option:selected").text();
    start_date = Date.parse($('#start-date-selector').datepicker( "getDate" ))/1000;
    end_date = Date.parse($('#end-date-selector').datepicker( "getDate" ))/1000;
    slider_value = $('#slider-value-selector').val();
    $('#visualization').html('');
    fourField(db_json, "visualization", x_dimension, y_dimension, r_dimension, start_date, end_date, slider_value);
  }

  $.ajax({
    url: "json"
  }).done(function(data) {
    db_json = data;

    // Collect number dimensions across projects in order of appearance
    var dimension_names = [];
    for (var i = 0, ilen = db_json.length; i < ilen; i++) {
      var project = db_json[i];
      for (var j = 0, jlen = project.dimensions.length; j < jlen; j++) {
        var dimension = project.dimensions[j];
        if (dimension.dimension_type == 'NumberDimension') {
          var name = dimension.dimension_object.name;
          if ($.inArray(name, dimension_names) == -1)
            dimension_names.push(name);
        }
      }
    }

    // Populate selectors, set first dimensions selected
    var axes = ['#x-selector', '#y-selector', '#r-selector'];
    for (var i = 0, ilen = axes.length; i < ilen; i++) {
      var selector = $(axes[i]);
      selector.html('<option>---</option>');
      for (var j = 0, jlen = dimension_names.length; j < jlen; j++) {
        var name = dimension_names[j];
        selector.append('<option value="'+name+'">'+name+'</option>');
        if (i == j)
          selector.val(name);
      }
      selector.prop('disabled', false);
    }
    change_if_all_selected();

    $("#start-date-selector").prop('disabled', false);
    $("#end-date-selector").prop('disabled', false);
    $("#slider-value-selector").prop('disabled', false);
  });

  $('#x-selector').on('change', change_if_all_selected);
  $('#y-selector').on('change', change_if_all_selected);
  $('#r-selector').on('change', change_if_all_selected);
  $('#start-date-selector').on('change', change_if_all_selected);
  $('#end-date-selector').on('change', change_if_all_selected);
  $('#slider-value-selector').on('change', change_if_all_selected);

  $('.datepicker').datepicker({'firstDay': 1, 'dateFormat': 'dd/mm/yy'});
});
