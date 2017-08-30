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
$(function(){
  $("#save-path-snap-btn").click(function(){
    project_id = $("#project-selector").val();
    x_dimension_ids = $("#x-selector").val();
    y_dimension_id = $("#y-selector").val();
    start_date = $("#start-date-selector").val();
    end_date = $("#end-date-selector").val();

    $("#path-snap-project-id").val(project_id);
    $("#path-snap-x-id").val(x_dimension_ids);
    $("#path-snap-y-id").val(y_dimension_id);
    $("#path-snap-start-date").val(start_date);
    $("#path-snap-end-date").val(end_date);
  });
});
