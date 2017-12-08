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
    organizations = $('#org-selector').val();
    associationtype = $('#type-selector').val();
    size = $('#size-selector').val();
    color = $('#color-selector').val();
    date = Date.parse($('#date-selector').datepicker( "getDate" ));

    $('#visualization').html('');
    dependencies(db_json, "visualization", organizations, associationtype, size, color, date);
    return;
  };

// Filter function to rule out duplicate values
  function onlyUnique(value, index, self) {
    return self.indexOf(value) === index;
  };

  $.ajax({
    url: "get_orgs"
  }).done(function(data) {
    data.forEach(function(elem) {
      return $('#org-selector').append('<option value="'+elem.id+'">'+elem.name+'</option>');
    });
    jQuery.noConflict();
    $('#org-selector').chosen();
    $('#org-selector').prop('disabled', false);
  });

  $.ajax({
    url: "json"
  }).done(function(data) {
    db_json = data;

    // Populate the selectors
    var numberic_names = [];
    var text_names = [];
    var associated_names = [];

    for (var i = 0, ilen = db_json.length; i < ilen; i++) {
      var project = db_json[i];
      for (var j = 0, jlen = project.dimensions.length; j < jlen; j++) {
        var dimension = project.dimensions[j];

        var name = dimension.dimension_object.name;
        if (dimension.dimension_type === 'NumberDimension') {
            numberic_names.push(name);
        } else if (dimension.dimension_type === 'AssociatedPersonDimension' ||
                   dimension.dimension_type === 'AssociatedPersonsDimension' ||
                   dimension.dimension_type === 'AssociatedProjectsDimension' ||
                   dimension.dimension_type === 'AssociatedOrganizationDimension') {
          associated_names.push(name);
        } else if (dimension.dimension_type === 'TextDimension') {
          text_names.push(name);
        }
      }
    }
    numberic_names = numberic_names.filter( onlyUnique );
    associated_names = associated_names.filter( onlyUnique );
    text_names = text_names.filter( onlyUnique );

    numberic_names.forEach(function(name) {
      return $('#size-selector').append('<option value="'+name+'">'+name+'</option>');
    });

    associated_names.forEach(function(name) {
      return $('#type-selector').append('<option value="'+name+'">'+name+'</option>');
    });

    text_names.forEach(function(name) {
      return $('#color-selector').append('<option value="'+name+'">'+name+'</option>');
    });


    $('#size-selector').prop('disabled', false);
    $('#type-selector').prop('disabled', false);
    $('#color-selector').prop('disabled', false);
    $('#date-selector').prop('disabled', false);

    dependencies(db_json, "visualization");
  });

  jQuery.noConflict();
  $('#org-selector').on('change', change_if_data_selected);
  $('#type-selector').on('change', change_if_data_selected);
  $('#size-selector').on('change', change_if_data_selected);
  $('#color-selector').on('change', change_if_data_selected);
  $('.datepicker').on('change', change_if_data_selected);

  $('.datepicker').datepicker({'firstDay': 1, 'dateFormat': 'dd/mm/yy'});

});
