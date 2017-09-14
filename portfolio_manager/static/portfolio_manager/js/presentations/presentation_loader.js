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

  $(".presentationVisualization").each( function(i) {
    var input =  $("#visualization-data"+ i.snap_type + i.id).data(),
        x = input['x'],
        y = input['y'],
        start = input['start'],
        end = input['end'],
        data = input['data']
        target = "visualization" + i.snap_type + i.id;

        if (i.snap_type == 'PA') {
          project_id = input['project']
          $.ajax({
            url: data
          }).done(function(data) {
            var db_json = data,
            x_dimension_ids = [];

            if ( typeof x == "string") {
            	if (x != "") {
                x_dimension_ids = x.trim().split(",");
              }
            } else {
              x_dimension_ids.push(x);
            }

            data_id_array = x_dimension_ids;
            data_id_array.unshift(y_dimension_id);
            data_id_array.unshift(project_id);

            $("#loading-icon").hide();
            generate_path_svg(
                  db_json,
                  "visualization",
                  data_id_array,
                  start,
                  end
                );
          });
        } else if (i.snap_type == 'FF') {
          r = input['r']
          zoom = input['zoom']

          $("#loading-icon").hide();
          fourField(data, target, x, y, r, start, end, zoom);
        }

  })


});
