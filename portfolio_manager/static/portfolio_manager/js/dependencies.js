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
  valueArray = [],
  nodeMap = new Map();

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
      var currentDimension = json[j].dimensions[i].dimension_object
      if (currentDimension.name === associationtype) {
        valueArray.push(nodeSize(json[j]))

        if (associationtype === "AssociatedProjectsDimension" && currentDimension.value != undefined) {
          currentDimension.value.map(function(x) {
            return valueArray.push(nodeSize(findProjectJson(x)));
          } )
        };
      };
    };
  };

  // defining denominator for scaling overly large values to usable size
  var denominator = 1;
  if (d3.max(valueArray) > 1000000) {
    denominator = d3.max(valueArray) / 100000;
  };

  // getting the current smallest value to be used as default size for people nodes
  var smallValue = d3.min(valueArray);

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
    index,
    sourceNode,
    targetNode;

    // Create source node, currently default is projects.
    sizeS = nodeSize(json[j])/ denominator;
    nameS = nodeName(json[j]);
    colorS = nodeColor(json[j], nodeColorValue);

    sourceNode = nodeMap.get("APD"+json[j].id) ||
                 nodeMap.set("APD"+json[j].id, {"shape": "circle","name": nameS, "value": sizeS / denominator, "color": colorS }).get("APD"+json[j].id)

    for (i = 0; i < size; i++) {
      /* Create target node(s) can be projects, people or organizations
       * for types that don't have desired arguments default values are
       * given. This is temporal solution before the backend version can
       * be implemented.
      */
      if ( json[j].dimensions[i].dimension_object.name === associationtype ) {
        var thisDimensionType = json[j].dimensions[i].dimension_type;

        if (thisDimensionType === "AssociatedProjectsDimension") {
          createAPDTargetNodes(sourceNode, json[j].dimensions[i].dimension_object.value);
        } else if (thisDimensionType === "AssociatedPersonsDimension") {
          createAPSTargetNodes(sourceNode, json[j].dimensions[i].dimension_object.value);
        }  else if (thisDimensionType === "AssociatedPersonDimension") {
          createAPTargetNode(sourceNode, json[j].dimensions[i].dimension_object.history[0].value);
        } else if (thisDimensionType === "AssociatedOrganizationDimension") {
          createAOTargetNode(sourceNode, json[j].dimensions[i].dimension_object.history[0].value);
        }
      };
    };
  };

  nodes = Array.from(nodeMap.values())

  // function to ditch duplicate values from a array.
  function uniq(a) {
    var seen = {};
    return a.filter(function(item) {
      return seen.hasOwnProperty(item) ? false : (seen[item] = true);
    });
  };

  // map connecting link amount with source node
  var linkWeightMap = new Map()

  for (elem in links) {
    var keyValue = links[elem].source
    if (!linkWeightMap.has(keyValue)) {
      linkWeightMap.set(keyValue, 1)
    } else {
      var newValue = linkWeightMap.get(keyValue) + 1
      linkWeightMap.set(keyValue, newValue)
    }
  }

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


  var values = nodes.map(x => x.value);

  //maximum and minimum value of the nodes
  var minDataPoint = d3.min(values);
  var maxDataPoint = d3.max(values);
  var minScealdeSize = 20;
  var maxScaledSize = 75;

  /* defining custom linearscale from minimum and maximum values of the nodes.
  * Makes possible to visualize large and small projects simultanously and
  * prevents situations where projects are too small or big for given canvas
  */
  var linearScale = d3.scaleLinear()
                      .domain([minDataPoint,maxDataPoint])
                      .range([minScealdeSize,maxScaledSize]);

  var opacityScale = d3.scalePoint()
                       .domain(uniq(Array.from(linkWeightMap.values()))
                                                            .sort(function(a,b) {
                                                              return a - b;
                                                            }))
                       .range([0.80, 0.15]);

  /* defining the graph force, for example default distance of balls and
  * aggressivity of charge of the balls
  */
  var force = d3.forceSimulation()
                .force('link', d3.forceLink().distance(maxScaledSize * 2))
                .force("collide",d3.forceCollide( function(d){return linearScale(d.value) + 10 }))
                .force("center", d3.forceCenter(width / 2, height / 2));



  // Timer for limiting the time and resources used for the visualization
  var forceTimer = d3.timeout(function(d) {
                    force.stop()
                    forceTimer.stop()
                  },7000);

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
                .attr("class", "link" )
                .attr("marker-end", "url(#end)")
                .style("opacity", function(d) { return opacityScale(linkWeightMap.get(d.source)); });

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
                .on("end", dragend)
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


  function tick() {
    // Takes care that balls don't get out of canvas by force
    node.attr("transform", function(d) {
      // It is OK to use 'validate' directly to force algorithm's results. On the next iteration cycle neighbors
      // just react to the new position and overlaps caused by this sudden move get fixed automatically.
      d.x = validate(d.x,0,width, linearScale(d.value)+ballOutline)
      d.y = validate(d.y,0,height, linearScale(d.value)+ballOutline)
      return "translate(" + d.x + "," + d.y + ")";
    });
    // add the curvy lines
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

  force.nodes(d3.values(nodes))
        .on("tick", tick);

  force.force("link")
        .links(links);

  function linedShape(d) {
    if (d.shape === "rotateRect"){
      return "rect"
    } else {
      return d.shape
    }
  }

  /* action to take on dragStart
  *  makes project name larger,
  * fixes the ball position and adds black outline for
  * positionally locked balls
  */
  function dragstart(d)  {
    forceTimer.stop()
    force.force("center", null);
    if (!d3.event.active) force.velocityDecay(0.4).alphaDecay(0.05).alphaTarget(0.20).restart();
    d3.select(this).select(linedShape(d)).transition()
      .style("stroke", "black")
      .style("stroke-width", ballOutline + "px");

    d3.select(this).select("text").transition()
      .duration(750)
      .attr("x", 22)
      .style("font-weight", "bold");
  };

  // dragend triggers the timer for the force, stopping the calculation after 5 seconds
  function dragend(d) {
    forceTimer.restart(function(d) {
      force.stop()
      forceTimer.stop()
    }, 5000);
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
    force.velocityDecay(0.4).alphaDecay(0.05).alphaTarget(0.20).restart();
  };

  // this function drags the node inside the height-width limits
  function onDrag(d) {
    d.fx = validate(d3.event.x, 0, width, linearScale(d.value)+ballOutline);
    d.fy = validate(d3.event.y, 0, height, linearScale(d.value)+ballOutline);
    force.tick()
  };

  /* helper function for "onDrag" and tick() to validate whether
  * the whole ball is within display box limits
  */
  function validate(x, a, b, radius) {
    if (x < a + radius) x = radius;
    if (x > b - radius) x = b - radius;
    return x;
  };

  function findProjectJson(id) {
    var projectJson;
    for (o = 0; o < jsonlen - 1; o++) {
      if (json[o].id === id) {
        projectJson = json[o];
      }
    }
    return projectJson;
  };
  // Functions that create nodes and links for different associantion types
  function createAPDTargetNodes(source, targetIdArray) {
    targetIdArray.map(function(x) {
      projectJson = findProjectJson(x);

      sizeT = nodeSize(projectJson)/ denominator;
      nameT = nodeName(projectJson);
      colorT = nodeColor(projectJson, nodeColorValue);

      targetNode = nodeMap.get("APD"+x) ||
      nodeMap.set("APD"+ x, {"shape": "circle", "name": nameT, "value": sizeT / denominator, "color": colorT}).get("APD"+x);

      links.push({"source": source, "target": targetNode});
    });
  };

  function createAPSTargetNodes(source, targetIdArray) {
    targetIdArray.map(function(x) {
      projectId = x.id
      sizeT = smallValue / denominator;
      nameT = x.first_name;
      colorT = nameT;

      targetNode = nodeMap.get("APS"+projectId) ||
      nodeMap.set("APS"+ projectId, {"shape": "rect", "name": nameT, "value": sizeT / denominator, "color": colorT}).get("APS"+projectId);

      links.push({"source": source, "target": targetNode});
    })
  };

  function createAPTargetNode(source, targetObject) {
    projectId = targetObject.id
    sizeT = smallValue / denominator;
    nameT = targetObject.first_name;
    colorT = nameT;

    targetNode = nodeMap.get("AP"+projectId) ||
    nodeMap.set("AP"+ projectId, {"shape": "rect", "name": nameT, "value": sizeT / denominator, "color": colorT}).get("AP"+projectId);


    links.push({"source": source, "target": targetNode});
  };

  function createAOTargetNode(source, targetObject) {
    projectId = targetObject.id
    sizeT = smallValue / denominator;
    nameT = targetObject.name;
    colorT = nameT;

    targetNode = nodeMap.get("AO"+projectId) ||
    nodeMap.set("AO"+ projectId, {"shape": "rotateRect", "name": nameT, "value": sizeT / denominator, "color": colorT}).get("AO"+projectId);

    links.push({"source": sourceNode, "target": targetNode});
  };

  /* searches the name of the project from the given json.
  * If name with given ID is not found returns empty string
  */
  function nodeName(jsonChunck) {

    for(l = 0; l < jsonChunck.dimensions.length ; l++ ){
      var name;
      if (jsonChunck.dimensions[l].dimension_object.name === "Name") {
        name = jsonChunck.dimensions[l].dimension_object.history[0].value
        if (name != undefined) {
          return name;
        };
      };
    };
    return "";
  };
  /* searches the size parameter of the project from the given json. if no such id is
  * found, or if the project doesn't have size parameter, returns 0
  */

  function nodeSize(jsonChunck) {
    var value;
    for(m = 0; m < jsonChunck.dimensions.length ; m++ ){
      if (jsonChunck.dimensions[m].dimension_object.name === nodeSizeValue) {
        value = jsonChunck.dimensions[m].dimension_object.history[0].value
        if (value != undefined) {
          return value;
        };
      };
    };
    return 0;
  };

  function nodeColor(jsonChunck, colorParameter) {
    var color;
    for (n = 0; n < jsonChunck.dimensions.length ; n++ ) {
      if (jsonChunck.dimensions[n].dimension_object.name === colorParameter) {
        color = jsonChunck.dimensions[n].dimension_object.history[0].value
        if (color != undefined) {
          return color;
        };
      };
    };
    return "";
  };
};
