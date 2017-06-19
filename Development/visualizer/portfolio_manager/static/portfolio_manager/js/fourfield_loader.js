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
    start_date = Date.parse($('#start-date-selector').val())/1000;
    end_date = Date.parse($('#end-date-selector').val())/1000;
    slider_value = $('#slider-value-selector').val();
    $('#visualization').html('');
    fourField(db_json, x_dimension, y_dimension, r_dimension, start_date, end_date, slider_value);
  }

  $.ajax({
    url: "json"
  }).done(function(data) {
    db_json = data;
    dimension_names = {};

    for (var i = 0, ilen = db_json.length; i < ilen; i++) {
      for(var j = 0, jlen = db_json[i].dimensions.length; j < jlen; j++) {
        dimension = db_json[i].dimensions[j];
        if(dimension.dimension_type == 'DecimalDimension'){
          dimension_names[dimension.dimension_object.name] = dimension.dimension_object.name;
        }
       }
    }

    $('#x-selector').html('<option>---</option>');
    $('#y-selector').html('<option>---</option>');
    $('#r-selector').html('<option>---</option>');

    for(var key in dimension_names) {
      $('#x-selector').append('<option value="'+key+'">'+dimension_names[key]+'</option>');
      $('#y-selector').append('<option value="'+key+'">'+dimension_names[key]+'</option>');
      $('#r-selector').append('<option value="'+key+'">'+dimension_names[key]+'</option>');
    }
    $("#x-selector").prop('disabled', false);
    $("#y-selector").prop('disabled', false);
    $("#r-selector").prop('disabled', false);
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
