$(function(){
  $.ajax({
    url: "json"
  }).done(function(data) {
    dependancies(data)
  });
});

function dependancies(json) {

	var nodes = {};

	var links = []
	var jsonlen = json.length
	console.log(json)
	var valueArray = [];

  /* Going through json input and collecting budget values from objects
   * that have values in ProjectDependencies. To be used in defining need
   * for denominaor != 1
  */
	for (j = 0; j < jsonlen; j++) {

		if (json[j].dimensions == undefined) {
			throw error("project dimensions missing");
		}

		var size = json[j].dimensions.length
		for (i = 0; i < size; i++) {
  		if (json[j].dimensions[i].dimension_object.name === "ProjectDependencies") {
  			valueArray.push(gimmeBudget(json[j].id))
  			if (json[j].dimensions[i].dimension_object.projects != undefined) {
  				valueArray.push(gimmeBudget(json[j].dimensions[i].dimension_object.projects[0]))
  			}
  		}
		}
	}
	
  // defining denominator for scaling overly large values to usable size
	var denominator = 1;
	if (d3.max(valueArray) > 1000000) {
	   denominator = d3.max(valueArray) / 100000;
	}

	// Compute the distinct nodes from the links. Each node is only created once
	for (j = 0; j < jsonlen; j++) {

		if(json[j].dimensions == undefined) {
			throw error("project dimensions missing");
		}

		var size = json[j].dimensions.length
		for (i = 0; i < size; i++) {
			if (json[j].dimensions[i].dimension_object.name === "ProjectDependencies") {
				for(p = 0; p < json[j].dimensions[i].dimension_object.projects.length;p++) {

					var budgetS = gimmeBudget(json[j].id) / denominator
					var budgetT = 0;
					var nameS = "";
					var nameT = gimmeName(json[j].dimensions[i].dimension_object.projects[p])

					if (json[j].dimensions[i].dimension_object.projects != undefined) {
						budgetT = gimmeBudget(json[j].dimensions[i].dimension_object.projects[p]) / denominator
					}

					if (json[j].dimensions[0].dimension_object.history != undefined) {
						nameS = gimmeName(json[j].id);
					}

					nameS = nodes[nameS] || (nodes[nameS] = {name: nameS, value: budgetS / denominator });
					nameT = nodes[nameT] ||
					  (nodes[nameT] = {name: nameT, value: budgetT / denominator});

					links.push({"source": nameS, "target": nameT, "budgetS":budgetS / denominator, "budgetT":budgetT / denominator})
					}
			}
		}
	}
	var values = [];
	var nameArray = [];
	var valueArray = [];
	var nodeValueArray = [];
	d3.values(nodes).forEach(function(node) {
		values.push(node.value)
		nameArray.push(node.name)
		nodeValueArray.push(node.name + " Budget: " + (node.value * denominator));
	});

	/* searches the name of the project with the given ID.
   * If name with given ID is not found returns empty string
  */
	function gimmeName(id) {

		for (z = 0; z < jsonlen; z++) {
			if (json[z].id == id) {
        for (m = 0; m < json[z].dimensions.length ; m++ ) {
					if (json[z].dimensions[m].dimension_object.name === "Name") {
						var name = json[z].dimensions[m].dimension_object.history[0].value
						if (name != undefined) {
							return name;
						} else {
							return "";
						}
					}
				}
			}
		}
		return "";
	}
	/* searches the budget of the project with the given ID. if no such id is
   * found, or if the project doesn't have budget, returns 0
  */
	function gimmeBudget(id) {
		for (z = 0; z < jsonlen; z++) {
			if (json[z].id == id) {
				for(m = 0; m < json[z].dimensions.length ; m++ ){
					if (json[z].dimensions[m].dimension_object.name === "SizeMoney") {
						var budget = json[z].dimensions[m].dimension_object.history[0].value
						if (budget != undefined) {
							return budget;
						} else {
							return 0;
						}
					}
				}
			}
		}
		return 0;
	}


	/* function to ditch duplicate values from a array. used in "names" since
   * links have duplicate nodes. works on strings only.
  */
	function uniq(a) {
		var seen = {};
		return a.filter(function(item) {
			return seen.hasOwnProperty(item) ? false : (seen[item] = true);
		});
	}
	// size of the display box and definition of colorscale (predefined ATM)
	var width = 960,
		height = 500,
		color = d3.scale.category20();

 // Ball outline is 3 pixels wide
  var ballOutline = 3;

	//maximum and minimum value of the nodes
	var minDataPoint = d3.min(values);
	var maxDataPoint = d3.max(values);

	/* defining custom linearscale from minimum and maximum values of the nodes.
   * Makes possible to visualize large and small projects simultanously and
   * prevents situations where projects are too small or big for given canvas
  */
	var linearScale = d3.scale.linear()
						          .domain([minDataPoint,maxDataPoint])
						          .range([20,75]);

	/* defining the graph force, for example default distance of balls and
   * aggressivity of charge of the balls
  */
	var force = d3.layout.force()
            		.nodes(d3.values(nodes))
            		.links(links)
            		.size([width, height])
            		.linkDistance(175)
            		.charge(-500)
            		.on("tick", tick)
            		.start();

	var drag = force.drag()
              		.on("dragstart", dragstart)
              		.on("drag", onDrag);

	// assign a type per value to encode opacity from css
	links.forEach(function(link) {
			link.type = "fivezero";
	});

	var svg = d3.select("body").append("svg")
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
            		.data(force.links())
            	  .enter().append("svg:path")
            		.attr("class", function(d) { return "link " + d.type; })
            		.attr("marker-end", "url(#end)");

	// define the nodes and their reactions
	var node = svg.selectAll(".node")
            		.data(force.nodes())
            	  .enter().append("g")
            		.attr("class", "node")
            		.on("click", click)
            		.on("dblclick", dblclick)
            		.on("dragstart", dragstart)
            		.call(force.drag);

	// add the nodes to canvas
	node.append("circle")
  		.attr("r", function(d) { return linearScale(d.value); })
  		.attr('fill-opacity', 0.7)
  		.style("fill", function(d) { return color(d.name); });

	// add the text, currently project name
	node.append("text")
  		.attr("x", 12)
  		.attr("dy", ".35em")
  		.text(function(d) { return d.name; });

	// add the curvy lines
	function tick() {
		// !!! browser inspection spews errors when (startX == endX && startY == endY) !!!
		path.attr("d", function(d) {
				// defining distance of two nodes
			var dx = (d.target.x - d.source.x) ,
  				dy = (d.target.y - d.source.y) ,
  				dr = Math.sqrt(dx * dx + dy * dy),
  				/* calculating the shortest distance between two circles
           * gives coordinates of start and end points
           */
  				startX = d.source.x + dx * linearScale(d.budgetS) / dr,
  				startY = d.source.y + dy * linearScale(d.budgetS) / dr,
  				endX = d.target.x - dx * linearScale(d.budgetT) / dr,
  				endY = d.target.y - dy * linearScale(d.budgetT) / dr;

			//Parsing the elliptical arc using previously calculated variables
			return "M" +
      				startX + "," +
      				startY + "A" +
      				dr + "," + dr + " 0 0,1 " +
      				endX + "," +
      				endY;
		});

    // Takes care that balls don't get out of canvas by force
		node.attr("transform", function(d) {
			var dx = validate(d.x,0,width, linearScale(d.value)+ballOutline)
			var dy = validate(d.y,0,height, linearScale(d.value)+ballOutline)
				return "translate(" + dx + "," + dy + ")";
		});
	}

  /* action to take on mouse click
  *  makes project name larger
  *  actions taken by dragStart append as well
  */

	function click() {
		d3.select(this).select("text").transition()
			.duration(750)
			.attr("x", 22)
			.style("stroke", "lightsteelblue")
			.style("stroke-width", ".5px")
			.style("font", "20px sans-serif");
		d3.select(this).select("circle").transition()
			.duration(750);
	}

	/* action to take on mouse double click
   * currently resizes text to normal and
   * releases ball position so it reacts to force again.
   * removes black outline
   */
	function dblclick(d) {
		d3.select(this).select("circle").transition()
			.duration(750)
			.attr("fixed", d.fixed = false)
			.style("stroke", "none");
		d3.select(this).select("text").transition()
			.attr("x", 12)
			.style("fill", "black")
			.style("stroke", "none")
			.style("font", "10px sans-serif");
	}

	/* action to take on dragstart,
   * actions taken on normal mouseclick append as well
   * currently fixes the ball position and adds black outline for
   * positionally locked balls
   */
	function dragstart(d) {
	  d3.select(this).select("circle").transition()
	  .attr("fixed", d.fixed = true)
	  .style("stroke", "black")
	  .style("stroke-width", "3px"); // Should be bind with ballOutline variable?
	}

	// this function drags the node inside the height-width limits
	function onDrag(d) {
	   d.px = validate(d.px, 0, width, linearScale(d.value)+ballOutline);
	   d.py = validate(d.py, 0, height, linearScale(d.value)+ballOutline);
	}

	/* helper function for "onDrag" and tick() to validate whether
   * the whole ball is within display box limits
   */
	function validate(x, a, b, radius) {
		if (x < a + radius) x = radius;
		if (x > b - radius) x = b - radius;
		return x;
	}

	/* The legend below the graph is given its own svg container in
   * which we have the project color, name and budget respectively.
   */
    var legendSpacing = 4;
    var legendRectSize = 25;
    var legendHeight = legendRectSize + legendSpacing;

    var svgLegend = d3.select("body")
                      .append("svg")
                      .attr("width", 300)
                      // Scaling the svg based on number of projects
                      .attr("height", (legendHeight)*(nameArray.length)+legendSpacing)
                      .append("g")
                      .attr("transform", "translate(0,"+(2*legendSpacing)+")");

    var legend = svgLegend.selectAll("legend")
                          .data(nameArray)
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
          .style("fill", function(d){return color(d)});

    legend.append("text")
          .data(nodeValueArray)
          .attr("x", legendRectSize + legendSpacing)
          .attr("y", legendRectSize - legendSpacing)
          .style("font", "16px sans-serif")
          .text(function(d){return ""+d+"€"});
}
