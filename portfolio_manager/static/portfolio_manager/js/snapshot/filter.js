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
