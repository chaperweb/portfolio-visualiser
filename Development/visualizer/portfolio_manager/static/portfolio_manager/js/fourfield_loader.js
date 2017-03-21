$(function() {
	$('#x-selector').append($('<option>', {value:1, text:"SizeMoney"}));
	$('#x-selector').append($('<option>', {value:2, text:"SizeManDays"}));
	$('#x-selector').append($('<option>', {value:3, text:"SizeEffect"}));
	
	$('#y-selector').append($('<option>', {value:1, text:"SizeMoney"}));
	$('#y-selector').append($('<option>', {value:2, text:"SizeManDays"}));
	$('#y-selector').append($('<option>', {value:3, text:"SizeEffect"}));
	
	$('#r-selector').append($('<option>', {value:1, text:"SizeMoney"}));
	$('#r-selector').append($('<option>', {value:2, text:"SizeManDays"}));
	$('#r-selector').append($('<option>', {value:3, text:"SizeEffect"}));
  $.ajax({
	

  });

function dimension_selector_change() {
  x_dimension = $('#x-selector').find("option:selected").text();
  y_dimension = $('#y-selector').find("option:selected").text();
  r_dimension = $('#r-selector').find("option:selected").text();

  
  if(x_dimension == "---" || y_dimension == "---" || r_dimension == "---") {
	//asdf
  } else if(y_dimension == x_dimension || y_dimension == r_dimension || x_dimension == r_dimension){
	  alert("ei saa olla samoja");
  } else {
	  d3.select("svg").remove();
	  fourField(x_dimension,y_dimension,r_dimension);
  }
}  

  
  /*
  $('#project-selector').on('change', function(){
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

            if (project.dimensions[j].dimension_type == 'DecimalDimension') {
              $('#x-selector').append('<option '+y_selected+' value="'+project.dimensions[j].id+'">'+project.dimensions[j].dimension_object.name+'</option>');
            }
            if (project.dimensions[j].dimension_type == 'DecimalDimension') {
              $('#y-selector').append('<option '+y_selected+' value="'+project.dimensions[j].id+'">'+project.dimensions[j].dimension_object.name+'</option>');
            }
          }
        }
        break;
      }
    }
    dimension_selector_change();
  });
  */
	$('#x-selector').on('change', dimension_selector_change);
	$('#y-selector').on('change', dimension_selector_change);
	$('#r-selector').on('change', dimension_selector_change);
});