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
  $("#save-fourfield-snap-btn").click(function(){
    x_dimension = $("#x-selector").find("option:selected").text();
    y_dimension = $("#y-selector").find("option:selected").text();
    r_dimension = $("#r-selector").find("option:selected").text();
    start_date = $("#start-date-selector").val();
    end_date = $("#end-date-selector").val();
    zoom = $("#slider-value-selector").find("option:selected").val();

    $("#fourfield-snap-x").val(x_dimension);
    $("#fourfield-snap-y").val(y_dimension);
    $("#fourfield-snap-r").val(r_dimension);
    $("#fourfield-snap-start-date").val(start_date);
    $("#fourfield-snap-end-date").val(end_date);
    $("#fourfield-snap-zoom").val(zoom);
  });
});
