$(function(){
  $.ajax({
    url: "json"
  }).done(function(data) {
    dependancies(data)
  });	
});

function dependancies(json) {
	
	//d3.json(json, function(error,json) {
	//if (error) throw error;
	var nodes = {};

	var links = []
	var jsonlen = json.length //shoud be generated range
	console.log(json)
	var valueArray = [];
	for (j = 0; j < jsonlen; j++) {
		
		if(json[j].dimensions == undefined) {
			throw error("project dimensions missing");
			//break; 
		}
		var size = json[j].dimensions.length
		for (i = 0; i < size; i++) {
		if (json[j].dimensions[i].dimension_object.name === "ProjectDependencies") {
			valueArray.push(gimmeBudget(json[j].id))
			if(json[j].dimensions[i].dimension_object.projects != undefined) {
				valueArray.push(gimmeBudget(json[j].dimensions[i].dimension_object.projects[0]))
			}
		}
		}
	}
	var denominator = 1;
	if(d3.max(valueArray) > 1000000) {
	denominator = d3.max(valueArray) / 100000;	
	}
	
	// Compute the distinct nodes from the links. Each node is only created once
	for (j = 0; j < jsonlen; j++) {
		
		if(json[j].dimensions == undefined) {
			throw error("project dimensions missing");
			//break; 
		}
		var size = json[j].dimensions.length
		for (i = 0; i < size; i++) {
		if (json[j].dimensions[i].dimension_object.name === "ProjectDependencies") {
			var budgetS = gimmeBudget(json[j].id) / denominator
			var budgetT = 0;
			if(json[j].dimensions[i].dimension_object.projects != undefined) {
				budgetT = gimmeBudget(json[j].dimensions[i].dimension_object.projects[0]) / denominator
			}
			var nameS = "";
			if(json[j].dimensions[0].dimension_object.history != undefined) {
				nameS = json[j].dimensions[0].dimension_object.history[0].value
			}
			var nameT = gimmeName(json[j].dimensions[i].dimension_object.projects[0])
		    json[j].id = nodes[json[j].id] ||
			(nodes[json[j].id] = {name: nameS, value: budgetS });
		    json[j].dimensions[i].dimension_object.projects[0] = nodes[json[j].dimensions[i].dimension_object.projects[0]] ||
			  (nodes[json[j].dimensions[i].dimension_object.projects[0]] = {name: nameT, value: budgetT });
		    links.push({"source": json[j].id, "target": json[j].dimensions[i].dimension_object.projects[0], "budgetS":budgetS, "budgetT":budgetT })
	   }
	  }
	}
	var values = [];
	var nameArray = [];
	var valueArray = [];
	nodevalueArray = [];
	d3.values(nodes).forEach(function(node) {
		values.push(node.value)
		nameArray.push(node.name)
		//valueArray.push(node.value)
		nodevalueArray.push(node.name + " " + (node.value * denominator));
	});
	/*
	if(d3.max(values) > 1000000) {
		var denominator = d3.max(values) / 100000
		d3.values(nodes).forEach(function(bignode) {
			bignode.value = bignode.value / denominator;
		});
		links.forEach(function(biglink) {
			biglink.budgetS = biglink.budgetS / denominator
			biglink.budgetT = biglink.budgetT / denominator;
		});
		values.forEach(function(value) {
			value = value / denominator;
		});
	}
	*/
	
	/*
	links.forEach(function(link) {
		json[j].id = nodes[json[j].id] ||
			(nodes[json[j].id] = {name: json[j].id, value: 200});
		json[j].dimensions[i].dimension_object.projects[0] = nodes[json[j].dimensions[i].dimension_object.projects[0]] ||
			(nodes[json[j].dimensions[i].dimension_object.projects[0]] = {name: json[j].dimensions[i].dimension_object.projects[0], value: 200});
		names.push(json[j].id.name + " " + 200) // adding names and valus to list below the graph
		names.push(json[j].dimensions[i].dimension_object.projects[0].name + " " + 200)
		values.push(200)
		values.push(200);
		// adding values to a array to scale the nodes correctly
	});
	*/
	/*
	function gimmeNameOld(id) {
	  return json[id-1].dimensions[0].dimension_object.history[0].value
	}
	*/

	// searches the name of the project with the given ID. currently relies on correct order of projects.
	function gimmeName(id) {
		
		for(z = 0; z < jsonlen; z++) {
			if(json[z].id == id) {
				var name = json[z].dimensions[0].dimension_object.history[0].value
				if (name != undefined) {
					return name;
				} else {
					return "";
				}
			}
		}
		return "";
	}
	// searches the budget of the project with the given ID. if no such id is found, or if the project doesn't have budget, returns 0
	function gimmeBudget(id) {	
		for(z = 0; z < jsonlen; z++) {
			if(json[z].id == id) {
				for(m = 0; m < json[z].dimensions.length ; m++ ){
					if(json[z].dimensions[m].dimension_object.name == "SizeMoney") {
						var budget = json[z].dimensions[m].dimension_object.history[0].value
						if (name != undefined) {
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
	

	// function to ditch duplicate values from a array. used in "names" since links have duplicate nodes. works on strings only
	function uniq(a) {
		var seen = {};
		return a.filter(function(item) {
			return seen.hasOwnProperty(item) ? false : (seen[item] = true);
		});
	}
	// size of the display box
	var width = 960,
		height = 500,
		color = d3.scale.category20b(); // this is the color scale. It scales colors

	//maximum and minimum value of the nodes	
	var minDataPoint = d3.min(values);
	var maxDataPoint = d3.max(values);

	//creating linearscale from minimum and maximum values of the nodes.
	var linearScale = d3.scale.linear()
						.domain([minDataPoint,maxDataPoint])
						.range([20,75]);
	// defining the graph
	var force = d3.layout.force()
		.nodes(d3.values(nodes))
		.links(links)
		.size([width, height])
		.linkDistance(175) // default distance of balls
		.charge(-500)
		.on("tick", tick)
		.start();
	var drag = force.drag()
		.on("dragstart", dragstart)
		.on("drag", onDrag);
	// Set the range
	var  v = d3.scale.linear().range([0, 100]);
	// Scale the range of the data
	v.domain([0, d3.max(links, function(d) { return d.value; })]);
	// asign a type per value to encode opacity
	links.forEach(function(link) {
			link.type = "fivezero";
	});
	var svg = d3.select("body").append("svg")
		.attr("width", width)
		.attr("height", height);
	// build the arrow.
	svg.append("svg:defs").selectAll("marker")
		.data(["end"])      // Different link/path types can be defined here
	  .enter().append("svg:marker")    // This section adds in the arrows
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
	// define the nodes
	var node = svg.selectAll(".node")
		.data(force.nodes())
	  .enter().append("g")
		.attr("class", "node")
		.on("click", click)
		.on("dblclick", dblclick)
		.on("dragstart", dragstart)
		.call(force.drag);
	// add the nodes
	node.append("circle")
		.attr("r", function(d) { return linearScale(d.value); })
		.attr('fill-opacity', 0.7)
		.style("fill", function(d) { return color(d.name); });
	// add the text
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
				//calculating the shortest distance between two circles
				startX = d.source.x + dx * linearScale(d.budgetS) / dr,
				startY = d.source.y + dy * linearScale(d.budgetS) / dr,
				endX = d.target.x - dx * linearScale(d.budgetT) / dr,
				endY = d.target.y - dy * linearScale(d.budgetT) / dr;
				//Parsing the elliptical arc
			return "M" +
				startX + "," +
				startY + "A" +
				dr + "," + dr + " 0 0,1 " +
				endX + "," +
				endY;
		});
		node
			.attr("transform", function(d) {
			var dx = validate(d.x,0,width, linearScale(d.value)+3)
			var dy = validate(d.y,0,height, linearScale(d.value)+3)
				return "translate(" + dx + "," + dy + ")";
		});
	}
	// action to take on mouse click
	function click() {
		d3.select(this).select("text").transition()
			.duration(750)
			.attr("x", 22)
			.style("stroke", "lightsteelblue")
			.style("stroke-width", ".5px")
			.style("font", "20px sans-serif");
		d3.select(this).select("circle").transition()
			.duration(750)
			//.attr('r', function (d) { return d.value/2; }) // resizing ball
			;
	}
	// action to take on mouse double click
	function dblclick(d) {
		d3.select(this).select("circle").transition()
			.duration(750)
			//.attr('r', function (d) { return d.value; }) // resizing ball
			.attr("fixed", d.fixed = false) // release ball position
			.style("stroke", "none");
		d3.select(this).select("text").transition()
			.attr("x", 12)
			.style("fill", "black")
			.style("stroke", "none")
			.style("font", "10px sans-serif");
	}
	// action on drag
	function dragstart(d) {
	  d3.select(this).select("circle").transition()
	  .attr("fixed", d.fixed = true) // fix ball position
	  .style("stroke", "black")
	  .style("stroke-width", "3px");
	}
	// Ball outline is 3 pixels wide
	var ballOutline = 3;
	// this function drags the node inside the height-width limits
	function onDrag(d) {
	   d.px = validate(d.px, 0, width, linearScale(d.value)+ballOutline);
	   d.py = validate(d.py, 0, height, linearScale(d.value)+ballOutline);
	}
	// helper function for "onDrag"
	function validate(x, a, b, radius) {
		if (x < a + radius) x = radius;
		if (x > b - radius) x = b - radius;
		return x;
	}
		// here the list of nodes is added below the graph.
		var ul = d3.select('body').append('ul');
			ul.selectAll('li')
			  .data(nodevalueArray)
			  .enter()
			  .append('li')
			  .html(String);
			  
			  
	/*
	console.log("Source: "+ json[j].id);
	console.log("Target: "+ json[j].dimensions[i].dimension_object.projects[0]);
	console.log(j + "," + i);
	*/
	//});
}
