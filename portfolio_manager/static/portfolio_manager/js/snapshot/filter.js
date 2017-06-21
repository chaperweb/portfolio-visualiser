$(function() {
  /* Make links trigger the togglebuttons */
  $('#path-filter-link').click(function(e){
    $('#path-filter-checkbox').bootstrapToggle('toggle');
  });
  $('#fourfield-filter-link').click(function(){
    $('#fourfield-filter-checkbox').bootstrapToggle('toggle');
  });

  /* To stop the button and link toggling */
  $('.toggle.ios').children().click(function(event) {
    event.stopPropagation();
    $(this).siblings().first().bootstrapToggle('toggle');
  });

  /* What happens on change */
  $('#path-filter-checkbox').change(function(e) {
    if ($(this).prop('checked')) {
      $('.path-snap').show();
    }
    else {
      $('.path-snap').hide();
    }
  });
  $('#fourfield-filter-checkbox').change(function(e) {
    if ($(this).prop('checked')) {
      $('.fourfield-snap').show();
    }
    else {
      $('.fourfield-snap').hide();
    }
  });
});
