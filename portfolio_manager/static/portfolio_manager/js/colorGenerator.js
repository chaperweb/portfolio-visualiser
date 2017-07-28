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

//basic colorscale for visualizations, codento colors at the moment
// orange, red, yellow, green, blue, grey
var colors = ["#f39911","#9f004d", "#fdca00","#61b020","#00708d","#757477"];

function enoughColors(amount, colourlist) {
  var colorsNow = colourlist.length;
  //if amount of colors and organizations match already give back the original colors
  if (amount === colorsNow) {
    return colourlist;
  }
  // If there are less organizations than colors drop the extra colors
  else if (amount < colorsNow) {
    var howMany = colorsNow - amount;
    var lessColors = colourlist.slice(0, howMany);
    return lessColors;
  }
  // If there are less colors than organizations generate some more colors
  // If amount is over 5 * colorsNow there might be problem.
  else {
    var moreColors = [];
    var modulo = amount % colorsNow
    if ( modulo === 0) {
      var extraNeeded = amount / colorsNow;
      for (color in colourlist) {
        moreColors = moreColors.concat( generateColours(extraNeeded, color));
      }
    } else {
      j = 0
      for (; j < modulo; j++) {
        var extraNeeded = Math.ceil(amount / colorsNow);
        moreColors = moreColors.concat(generateColours(extraNeeded, colourlist[j]));
      }
      while (j < colorsNow) {
        moreColors = moreColors.concat(generateColours(extraNeeded - 1, colourlist[j]));
        j++;
      }
    }
    return moreColors;
  }
};

//function for generating more colors
// The generated colours are based on given colour
function generateColours(integer, colour) {

  // Array for the return value and rgb version of the input color
  var allCol = []
  var mycol = d3.rgb(colour)

  // If there is just one color needed, return the original
  if (integer === 1) {
    allCol.push(mycol);
    return allCol;
  }

  // defining the 'distance' between generated colors centrifying the base color
  var step = Math.round(256 / integer)
  var up = (Math.round(integer / 2))

  if (integer % 2 == 0) {
    up++
  }

  //max and min for the color rgb values
  var rmax = Math.min(255, mycol.r + (up - 1) * step)
  var gmax = Math.min(255, mycol.g + (up - 1) * step)
  var bmax = Math.min(255, mycol.b + (up - 1) * step)
  var rmin = Math.max(0, mycol.r - (up - 1) * step)
  var gmin = Math.max(0, mycol.g - (up - 1) * step)
  var bmin = Math.max(0, mycol.b - (up - 1) * step)

  // temporal variable for the color generating puroposes
  var tempCol = mycol

  /* Algorithm for generating extra colors based on given seed color.
   *
   * If sum of the r,g and b values is less than 383 it will try to maximize the
   * given values one by one.
   * If the sum of the given values is more than 383 it will reduce the given values
   *
   * This could be more intelligent, but works mostly ok at the moment.
   */
  if (mycol.r + mycol.g + mycol.b < 383) {
    for (i = 1; i <= integer; i++) {
        if (tempCol.b < bmax) {
          tempCol = d3.rgb(mycol.r, mycol.g, Math.min(255, Math.max(mycol.b + ((i % up) * step), 0)))
          if (tempCol.b == bmax) bmax = mycol.b
        }
        else if (tempCol.g < gmax) {
          tempCol = d3.rgb(mycol.r, Math.min(255, Math.max(mycol.g + ((i % up) * step), 0)), mycol.b)
          if (tempCol.g == gmax) gmax = mycol.g
        }
        else if (tempCol.r < rmax) {
          tempCol = d3.rgb(Math.min(255, Math.max(mycol.r + ((i % up) * step), 0)), mycol.g, mycol.b)
          if (tempCol.r == rmax) rmax = mycol.r
        }

      allCol.push(tempCol.toString())
    }
  } else {
    for (i = 1; i <= integer; i++) {
        if (tempCol.b > bmin) {
          tempCol = d3.rgb(mycol.r, mycol.g, Math.min(255, Math.max(mycol.b - ((i % up) * step), 0)))
          if (tempCol.b == bmin) bmin = mycol.b
        }
        else if (tempCol.g > gmin) {
          tempCol = d3.rgb(mycol.r, Math.min(255, Math.max(mycol.g - ((i % up) * step), 0)), mycol.b)
          if (tempCol.g == gmin) gmin = mycol.g
        }
        else if (tempCol.r > rmin) {
          tempCol = d3.rgb(Math.min(255, Math.max(mycol.r - ((i % up) * step), 0)), mycol.g, mycol.b)
          if (tempCol.r == rmin) rmin = mycol.r
        }

      allCol.push(tempCol.toString())
    }
  }
  //return array of colors based on the given color
  return allCol;
};
