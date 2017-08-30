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

  var djdata = $("#dj-data").data(),
  start_date = Date.parse(djdata['start']),
  end_date = Date.parse(djdata['end']),
  project_id = djdata['project'],
  y_dimension_id = djdata['y']
  x_dimension_ids = djdata['x'].trim().split(",")
  data_url = djdata['url'];
//console.log(djdata)

  $.ajax({
    url: data_url
  }).done(function(data) {
    var db_json = data;

    data_id_array = x_dimension_ids;
    data_id_array.unshift(y_dimension_id);
    data_id_array.unshift(project_id);

        $("#loading-icon").hide();

  	generate_path_svg(
          db_json,
          "visualization",
          data_id_array,
          start_date,
          end_date
        );

    $("#projectPanel").html($("#projectName").text())
    $(".pathXlabel").each( function(i) {
      $("#xPanel").html($("#xPanel").html() + this.textContent + "<br>");
    })
    $("#yPanel").html($("#yAxisLabel").text())

  });


});
