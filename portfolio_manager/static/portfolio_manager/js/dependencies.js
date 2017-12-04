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
function dependencies(json, target, organizations, associationtype, nodeSizeValue, nodeColorValue, date) {
  var nodes = [],
  links = [],
  jsonlen = json.length,
  valueArray = [];

  /* Going through json input and collecting size values from objects
  * that have values in dependencies. To be used in defining need
  * for denominator != 1
  */
  for (j = 0; j < jsonlen; j++) {
    if (json[j].dimensions == undefined) {
      throw error("project dimensions missing");
    };

    var size = json[j].dimensions.length
    for (i = 0; i < size; i++) {
      if (json[j].dimensions[i].dimension_object.name === associationtype) {
        valueArray[json[j].id] = nodeSize(json[j].id)

        if (json[j].dimensions[i].dimension_object.value != undefined) {
          for (p = 0; p < json[j].dimensions[i].dimension_object.value.length; p++) {
            valueArray[json[j].dimensions[i].dimension_object.value[p]] = nodeSize(json[j].dimensions[i].dimension_object.value[p])
          }
        };
      };
    };
  };

  // defining denominator for scaling overly large values to usable size
  var denominator = 1;
  if (d3.max(valueArray) > 1000000) {
    denominator = d3.max(valueArray) / 100000;
  };

  // Compute the distinct nodes. Each node is only created once
  for (j = 0; j < jsonlen - 1; j++) {

    if(json[j].dimensions == undefined) {
      throw error("project dimensions missing");
    };

    var size = json[j].dimensions.length,
    sizeS,
    sizeT,
    nameS,
    nameT,
    colorS,
    colorT,
    sourceNode,
    targetNode;

    for (i = 0; i < size; i++) {
      // Create source node, currently default is projects.
      sizeS = nodeSize(json[j].id)/ denominator;
      nameS = "";
      colorS = nodeColor(json[j].id, nodeColorValue)

      if (json[j].dimensions[0].dimension_object.history != undefined) {
        nameS = nodeName(json[j].id);
      };
      sourceNode = nodes[json[j].id] ||
                  (nodes[json[j].id] = {"shape": "circle","name": nameS, "value": sizeS / denominator, "color": colorS });

      /* Create target node(s) can be projects, people or organizations
       * for types that don't have desired arguments default values are
       * given. This is temporal solution before the backend version can
       * be implemented.
      */
      if ( json[j].dimensions[i].dimension_object.name === associationtype ) {
        var thisDimensionType = json[j].dimensions[i].dimension_type

        if (thisDimensionType === "AssociatedProjectsDimension") {
          for(p = 0; p < json[j].dimensions[i].dimension_object.value.length;p++) {
            sizeT = nodeSize(json[j].dimensions[i].dimension_object.value[p])/ denominator;
            nameT = nodeName(json[j].dimensions[i].dimension_object.value[p]);
            colorT = nodeColor(json[j].dimensions[i].dimension_object.value[p], nodeColorValue)

            targetNode = nodes[json[j].dimensions[i].dimension_object.value[p]] ||
            (nodes[json[j].dimensions[i].dimension_object.value[p]] = {"shape": "circle", "name": nameT, "value": sizeT / denominator, "color": colorT});

            links.push({"source": sourceNode, "target": targetNode});
          };
        } else if (thisDimensionType === "AssociatedPersonsDimension") {
          for(p = 0; p < json[j].dimensions[i].dimension_object.value.length;p++) {

            sizeT = 100 / denominator;
            nameT = json[j].dimensions[i].dimension_object.value[p].first_name;
            colorT = nameT

            targetNode = nodes[json[j].dimensions[i].dimension_object.value[p].id] ||
            (nodes[json[j].dimensions[i].dimension_object.value[p].id] = {"shape": "rect", "name": nameT, "value": sizeT / denominator, "color": colorT});

            links.push({"source": sourceNode, "target": targetNode});
          };
        }  else if (thisDimensionType === "AssociatedPersonDimension") {

          sizeT = 100 / denominator;
          nameT = json[j].dimensions[i].dimension_object.history[0].value.first_name;
          colorT = nameT

          targetNode = nodes[json[j].dimensions[i].dimension_object.history[0].value.id] ||
          (nodes[json[j].dimensions[i].dimension_object.history[0].value.id] = {"shape": "rect", "name": nameT, "value": sizeT / denominator, "color": colorT});

          links.push({"source": sourceNode, "target": targetNode});
        } else if (thisDimensionType === "AssociatedOrganizationDimension") {
          sizeT = 100 / denominator;
          nameT = json[j].dimensions[i].dimension_object.history[0].value.name;
          colorT = nameT

          targetNode = nodes[json[j].dimensions[i].dimension_object.history[0].value.id] ||
          (nodes[json[j].dimensions[i].dimension_object.history[0].value.id] = {"shape": "rotateRect", "name": nameT, "value": sizeT / denominator, "color": colorT});

          links.push({"source": sourceNode, "target": targetNode});
        }
      };
    };
  };

  /* searches the name of the project with the given ID.
  * If name with given ID is not found returns empty string
  */
  function nodeName(id) {

    for (z = 0; z < jsonlen; z++) {
      if (json[z].id == id) {
        for (m = 0; m < json[z].dimensions.length ; m++ ) {
          if (json[z].dimensions[m].dimension_object.name === "Name") {
            var name = json[z].dimensions[m].dimension_object.history[0].value
            if (name != undefined) {
              return name;
            } else {
              return "";
            };
          };
        };
      };
    };
    return "";
  };
  /* searches the size parameter of the project with the given ID. if no such id is
  * found, or if the project doesn't have size parameter, returns 0
  */
  function nodeSize(id) {
    for (z = 0; z < jsonlen; z++) {
      if (json[z].id == id) {
        for(m = 0; m < json[z].dimensions.length ; m++ ){
          if (json[z].dimensions[m].dimension_object.name === nodeSizeValue) {
            var value = json[z].dimensions[m].dimension_object.history[0].value
            if (value != undefined) {
              return value;
            } else {
              return 0;
            };
          };
        };
      };
    };
    return 0;
  };
  function nodeColor(id, colorParameter) {

    for (z = 0; z < jsonlen; z++) {
      if (json[z].id == id) {
        for (n = 0; n < json[z].dimensions.length ; n++ ) {
          if (json[z].dimensions[n].dimension_object.name === colorParameter) {
            var color = json[z].dimensions[n].dimension_object.history[0].value
            if (color != undefined) {
              return color;
            } else {
              return "";
            };
          };
        };
      };
    };
    return "";
  };

  // function to ditch duplicate values from a array.
  function uniq(a) {
    var seen = {};
    return a.filter(function(item) {
      return seen.hasOwnProperty(item) ? false : (seen[item] = true);
    });
  };

  var colorArray = uniq(nodes.map(x => x.color))
  // size of the display box and definition of colorscale (predefined ATM)
  var width = $('#'+ target).width(),
      height = Math.max(600, $('#'+ target).height()),
      projecDependancyColors = enoughColors(colorArray.length, colors),
      colorScale = d3.scaleOrdinal()
                     .domain(d3.values(colorArray))
                     .range(projecDependancyColors);

  // Ball outline is 1 pixels wide
  var ballOutline = 1;


  var values = nodes.map(x => x.value)

  //maximum and minimum value of the nodes
  var minDataPoint = d3.min(values);
  var maxDataPoint = d3.max(values);

  /* defining custom linearscale from minimum and maximum values of the nodes.
  * Makes possible to visualize large and small projects simultanously and
  * prevents situations where projects are too small or big for given canvas
  */
  var linearScale = d3.scaleLinear()
                      .domain([minDataPoint,maxDataPoint])
                      .range([20,75]);

  /* defining the graph force, for example default distance of balls and
  * aggressivity of charge of the balls
  */
  var force = d3.forceSimulation()
                .force('link', d3.forceLink().id(function(d){ return d.name }).distance(100))
                .force("collide",d3.forceCollide( function(d){return linearScale(d.value) + 8 }))
                .force("charge", d3.forceManyBody().strength(-50))
                .force("center", d3.forceCenter(width / 2, height / 2));

  // assign a type per value to encode opacity from css
  links.forEach(function(link) {
    link.type = "fivezero";
  });

  var svg = d3.select("#" + target)
              .append("svg")
              .attr("width", width)
              .attr("height", height);

  // build the arrow.
  svg.append("svg:defs").selectAll("marker")
                        .data(["end"])      // Different link/path types can be defined here
                        .enter().append("svg:marker")    // This section adds in the arrowheads
                        .attr("id", String)
                        .attr("viewBox", "0 -5 10 10")
                        .attr("refX", 10)
                        .attr("refY", 0)
                        .attr("markerWidth", 10)
                        .attr("markerHeight", 10)
                        .attr("orient", "auto")
                        .append("svg:path")
                        .attr("d", "M0,-5L10,0L0,5");

  // add the links and the arrows
  var path = svg.append("svg:g").selectAll("path")
                .data(links)
                .enter().append("svg:path")
                .attr("class", function(d) { return "link " + d.type; })
                .attr("class", "link" )
                .attr("marker-end", "url(#end)");

  // define the nodes and their reactions
  var node = svg.selectAll(".node")
                .data(d3.values(nodes))
                .enter().append("g")
                .attr("class", "node")
                .style("fill", function(d) { return colorScale(d.color); })
                .attr('fill-opacity', 0.8)
                .on("dblclick", dblclick)
                .call(d3.drag()
                .on("start", dragstart)
                .on("drag", onDrag));


  /* Draws the shape of the node based on the given value
   * rectangles are translated to central coordinates as their
   * initial coordinates locate the central point to the left top
   * corner of the rectangle.
   */
  node.filter(function(d) {return d.shape === "circle"})
      .append("circle")
      .attr("r", function(d) { return linearScale(d.value); });

  node.filter(function(d) {return d.shape === "rect"})
      .append("rect")
      .attr("height", function(d) { return linearScale(d.value); })
      .attr("width", function(d) { return linearScale(d.value); })
      .attr("transform",  function(d) {
        var trans = (linearScale(d.value) / 2)
        return "translate(-" + trans + ",-" + trans +")";});

  node.filter(function(d) {return d.shape === "rotateRect"})
      .append("rect")
      .attr("height", function(d) { return linearScale(d.value); })
      .attr("width", function(d) { return linearScale(d.value); })
      .attr("transform",  function(d) {
        var trans = (linearScale(d.value) / 2)
        return "rotate(45) translate(-" + trans + ",-" + trans +") ";});

// add the text, currently project name
  node.append("text")
      .attr("x", 12)
      .attr("text-anchor", "middle")
      .attr("dy", ".35em")
      .text(function(d) { return d.name; });

  // add the curvy lines
  function tick() {
    // Takes care that balls don't get out of canvas by force
    node.attr("transform", function(d) {
      // It is OK to use 'validate' directly to force algorithm's results. On the next iteration cycle neighbors
      // just react to the new position and overlaps caused by this sudden move get fixed automatically.
      d.x = validate(d.x,0,width, linearScale(d.value)+ballOutline)
      d.y = validate(d.y,0,height, linearScale(d.value)+ballOutline)
      return "translate(" + d.x + "," + d.y + ")";
    });

    path.attr("d", function(d) {
      // defining distance of two nodes
      var dx = (d.target.x - d.source.x) ,
      dy = (d.target.y - d.source.y) ,
      // avoid division by zero by never allowing dr to be 0,
      dr = (dx == 0 && dy == 0) ? 0.1 : Math.sqrt(dx * dx + dy * dy),
      /* calculating the shortest distance between two circles
      * gives coordinates of start and end points
      */
      startX = d.source.x + dx * linearScale(d.source.value) / dr,
      startY = d.source.y + dy * linearScale(d.source.value) / dr,
      endX = d.target.x - dx * linearScale(d.target.value) / dr,
      endY = d.target.y - dy * linearScale(d.target.value) / dr,
      /* we need a third point for quadratic curve. Assume a straight line between startXY and endXY.
      * Start from the middle point of that line, and take a point that is at right angle towards that point at
      * distance line_length / 2. It is easy to calculate a line at the right angle towards the original line:
      * just switch X and Y component of the original line and negate one of them. No trigonometry needed!
      */
      midX = (startX + endX) / 2 - (startY - endY) / 4,
      midY = (startY + endY) / 2 + (startX - endX) / 4;
      /* then make sure that control point stays within the visible area */
      if (midX < 0) {
        midX = 0;
      } else if (midX > width) {
        midX = width;
      };
      if (midY < 0) {
        midY = 0;
      } else if (midY > height) {
        midY = height;
      };
      return "M " + startX + ", " + startY + " Q " + midX + ", " + midY + ", " + endX + ", " + endY;
    });

  };
  force
  .nodes(d3.values(nodes))
  .on("tick", tick);

  force.force("link")
  .links(links);

  /* action to take on dragStart
  *  makes project name larger,
  * fixes the ball position and adds black outline for
  * positionally locked balls
  */

  function linedShape(d) {
    if (d.shape === "rotateRect"){
      return "rect"
    } else {
      return d.shape
    }
  }

  function dragstart(d)  {
    if (!d3.event.active) force.alphaTarget(0.3).restart();
    d3.select(this).select(linedShape(d)).transition()
      .style("stroke", "black")
      .style("stroke-width", ballOutline + "px");

    d3.select(this).select("text").transition()
      .duration(750)
      .attr("x", 22)
      .style("font-weight", "bold");
  };

  /* action to take on mouse double click
  * currently resizes text to normal and
  * releases ball position so it reacts to force again.
  * removes black outline
  */
  function dblclick(d) {

    d3.select(this).select(linedShape(d)).transition()
    .duration(750)
    .style("stroke", "none");
    d.fx = null
    d.fy = null
    d3.select(this).select("text").transition()
    .style("font-weight", "normal");
  };

  // this function drags the node inside the height-width limits
  function onDrag(d) {
    d.fx = validate(d3.event.x, 0, width, linearScale(d.value)+ballOutline);
    d.fy = validate(d3.event.y, 0, height, linearScale(d.value)+ballOutline);
  };

  /* helper function for "onDrag" and tick() to validate whether
  * the whole ball is within display box limits
  */
  function validate(x, a, b, radius) {
    if (x < a + radius) x = radius;
    if (x > b - radius) x = b - radius;
    return x;
  };

  /* The legend next to the graph is given its own svg container in
  * which we have the project color, name and budget respectively.

  var textWidth = []

  svg.append("g")
  .selectAll("legend")
  .data(d3.values(nodes))
  .enter()
  .append("text")
  .text(function(d) {return d.name})
  .each(function(d,i){
    var thisWidth = Math.max(1,this.getComputedTextLength())
    textWidth.push(thisWidth)
    $(this).remove();
  });

  maxTextLength = d3.max(textWidth)
  var legendSpacing = 4;
  var legendRectSize = 25;
  var legendWidth = maxTextLength + legendRectSize + 10
  var legendHeight = legendRectSize + legendSpacing;

  var svgLegend = d3.select("#" + target)
                    .append("svg")
                    .attr("width", legendWidth)
                    // Scaling the svg based on number of projects
                    .attr("height", (legendHeight)*(d3.values(nodes).length)+legendSpacing)
                    .append("g")
                    .attr("transform", "translate(0,"+(2*legendSpacing)+")");

  var legend = svgLegend.selectAll("legend")
                        .data(d3.values(nodes))
                        .enter()
                        .append("g")
                        .attr("transform", function(d,i){
                          // Offsetting the legend lines from each other
                          var offsetX = legendSpacing
                          var offsetY = i * legendHeight - offsetX
                          return "translate("+offsetX+","+offsetY+")"
  });

  legend.append("rect")
        .attr("width", legendRectSize)
        .attr("height", legendRectSize)
        .style("fill", function(d){return colorScale(d.color)});

  legend.append("text")
        .attr("x", legendRectSize + legendSpacing)
        .attr("y", legendRectSize - legendSpacing)
        .text(function(d){
          return d.name;
  });
    */
};
