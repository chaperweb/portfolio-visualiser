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
  var djdata = $("#dj-data").data(),
      x = djdata['x'],
      y = djdata['y'],
      r = djdata['r'],
      start = Date.parse(djdata['start'])/1000,
      end = Date.parse(djdata['end'])/1000,
      zoom = djdata['zoom'],
      data = djdata['data'];

  $("#loading-icon").hide();
  fourField(data, x, y, r, start, end, zoom);
});
