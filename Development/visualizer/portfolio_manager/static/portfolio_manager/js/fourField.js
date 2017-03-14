$(function(){
  $.ajax({
    url: "json"
  }).done(function(data) {
    fourField(data)
  });	
});
function fourField(json) {
	//d3.json('outputData.json', function(error,json) {
	//if (error) throw error;
		console.log(json);
	var projects = []
	//console.log(json[8].dimensions[0].dimension_object.name);
		var xToBe = "SizeMoney"
		var yToBe = "SizeManDays"
		var radToBe = "SizeEffect"
		var jsonlen = json.length
		var projects = []
		var data = [{"X": xToBe, "Y": yToBe}]
		for (j = 0; j < jsonlen; j++) {
			var size = json[j].dimensions.length
			var inProgress = {"name": json[j].name, "organization": "", "xAxisActual": [],"xAxisPlanned": [],"xAxis": 0,"radius":[],"yAxisActual":[],"yAxisPlanned":[],"yAxis":0};
			var xID = 0
			var yID = 0			
			for (i = 0; i < size; i++) {
		    if (json[j].dimensions[i].dimension_type == 'DecimalDimension' ) {

					var collectVal = []
					var historyLen = json[j].dimensions[i].dimension_object.history.length;
					for (h = 0; h < historyLen; h++) {
						var date = json[j].dimensions[i].dimension_object.history[h].history_date;
						var planned = json[j].dimensions[i].dimension_object.history[h].value;
						//var actual = json[j].dimensions[i].dimension_object.history[h].value; // hardcoded since there is no milestones
						var parsedDate = new Date(date).getTime() / 1000
						collectVal.push([parsedDate, planned])
						//console.log(collectVal);
					};
					var valueName = json[j].dimensions[i].dimension_object.name;
					if ( valueName === xToBe) {
						xID = json[j].dimensions[i].id
						inProgress.xAxisActual = (collectVal).reverse();
					} else if (valueName === yToBe) {
						yID = json[j].dimensions[i].id
						inProgress.yAxisActual = (collectVal).reverse();
					} else if (valueName === radToBe) {
						inProgress.radius =(collectVal)
					}
				} else if (json[j].dimensions[i].dimension_type === 'AssociatedOrganizationDimension' ) {
					inProgress.organization = json[j].dimensions[i].dimension_object.history[0].value.name
				};
				
			}
			//console.log(xID)
			//console.log(yID)
		var collectXPlan = []
		var collectYPlan = []
		if(json[j].milestones != undefined) {

			for(e = 0; e < json[j].milestones.length ; e++ ) {
				if(json[j].milestones[e].history[0].dimensions != undefined) {
				for(q = 0; q < json[j].milestones[e].history[0].dimensions.length ; q++ ) {
					console.log(json[j].milestones[e].history[0].dimensions[q].project_dimension)
						if(json[j].milestones[e].history[0].dimensions[q].project_dimension == xID) {
							//lisää X
							var date = json[j].milestones[e].history[0].due_date
							var parsedDate = new Date(date).getTime() / 1000
							var milestoneValue = json[j].milestones[e].history[0].dimensions[q].dimension_milestone_object.value
							console.log(milestoneValue)
							collectXPlan.push([parsedDate,milestoneValue])
						} else if( json[j].milestones[e].history[0].dimensions[q].project_dimension == yID ) {
							// lisää Y
							var date = json[j].milestones[e].history[0].due_date
							var parsedDate = new Date(date).getTime() / 1000
							var milestoneValue = json[j].milestones[e].history[0].dimensions[q].dimension_milestone_object.value
							console.log(milestoneValue)
							collectYPlan.push([parsedDate,milestoneValue])
						}
					}
				}
			}
		
			
				
		inProgress.xAxisPlanned =(collectXPlan)
		inProgress.yAxisPlanned =(collectYPlan)	
		projects.push(inProgress);			
		}

	}
console.log(projects);
	function x(d) {
		if(d.xAxis > 0) { return (width/2-d.xAxis*xTimes + sliderValues*xTimes);
		} else {return (width/2-d.xAxis*xTimes - sliderValues*xTimes)}
	}
	function y(d) {
		if(d.yAxis > 0) {return (d.yAxis*yTimes + height/2 - sliderValues*yTimes);
		} else {return (d.yAxis*yTimes + height/2 + sliderValues*yTimes);}
	}
	function radius(d) {
		if (d.xAxis !== 0 && d.yAxis !== 0 && d.yAxis !== -Infinity && d.yAxis !== Infinity && d.xAxis !== Infinity && d.xAxis !== -Infinity) {
			return d.radius;
		} else {
			d.radius = 0
			return d.radius;
		}
	}
	function color(d) { return d.organization; }
	function key(d) { return d.name; }

	console.log()


	// size of the display box
	var width = 1000,
		height = 1000,
		margin = {right: width * 0.1, left: width * 0.1, top: height * 0.1, bottom: 50},
		axisLenghtX = width * 0.8,
		axisLenghtY = height * 0.8,
		sliderY = height - margin.bottom
		sliderValues = 100		
		xTimes = axisLenghtX/(2*sliderValues) // 200 is the amount of the % in the graph (100 - (-100))
		yTimes = axisLenghtY/(2*sliderValues) // 200 is the amount of the % in the graph (100 - (-100))


	var startDate = 1419465600
	var endDate = 1480464000

	// The scales for the x and y axis.
	//range means the length of the line and domain the numbers beneath it
	var scaleX = d3.scaleLinear()
				   .range([0,axisLenghtX])
				   .domain([-100,100]);

	var scaleY = d3.scaleLinear()
				   .range([0,axisLenghtY])
				   .domain([100,-100]);

	var colorScale = d3.scaleOrdinal(d3.schemeCategory10);

	//container for everything
	var svg = d3.select("body").append("svg")
				.attr("width", width)
				.attr("height", height);

	//Parser for a human readable date format dd. mm. yyyy
	var parseDate = d3.timeFormat("%d. %m. %Y");

	// Add the date label; the value is set on transition.
	var dateLabel =  svg.append("text")
						.attr("class", "currentDate")
						.attr("text-anchor", "end")
						.attr("y", height - 100)
						.attr("x", width )
						.text(parseDate((new Date(startDate*1000))));

	//slider start & stop values
	var labelStart = parseDate(startDate * 1000)
	var labelEnd = parseDate(endDate * 1000)
	var sSLabel = svg.append("text")
					 .attr("class", "sliderLabel")
					 .attr("text-anchor", "start")
					 .attr("x", 0)
					 .attr("y", height)
					 .text("Start date: " + labelStart);

	var sELabel = svg.append("text")
					.attr("class", "sliderLabel")
					.attr("text-anchor", "end")
					.attr("x", width)
					.attr("y", height)
					.text("End date: " + labelEnd);
	//label for project-name. visible when cursor is hovered over the circle representing the project
	var namelabel =  svg.append("text")
						.attr("class", "info")
						.attr("text-anchor", "start")
						.attr("y", 80)
						.attr("x", 20)
						.text("");

	//label for the organizations
	var orglabel = svg.append("text")
					  .attr("class", "info")
					  .attr("text-anchor", "start")
					  .attr("y", 140)
					  .attr("x", 20)
					  .text("");
	//label for x-axis
	var xlabel = svg.append("text")
					  .attr("class", "axisLabel")
					  .attr("text-anchor", "start")
					  .attr("y", 240)
					  .attr("x", 20)
					  .text("x-axis: "+data[0].X);
	//label for y-axis
	var ylabel = svg.append("text")
					  .attr("class", "axisLabel")
					  .attr("text-anchor", "start")
					  .attr("y", 340)
					  .attr("x", 20)
					  .text("y-axis: "+data[0].Y);

	var bisect = d3.bisector(function(d) { return d[0]; });

	// Place and colorise circles, and define mouseenter and mouseleave functions
	var dot = svg.append("g")
				  .attr("class", "dots")
				  .selectAll(".dot")
				  .data(interpolateData(startDate))
				  .enter().append("circle")
				  .attr("class", "dot")
					.attr("name", function(d) { return d.name;})
					.attr('fill-opacity', 0.8)
				  .style("fill", function(d) { return colorScale(color(d)); })
				  .call(position)
					.sort(order)
					.on("mouseenter", function(d) {
						namelabel.text(d.name);
						orglabel.text(d.organization);
						dot.style("opacity", .4)
						d3.select(this).style("opacity", 1)
						d3.selectAll(".selected").style("opacity", 1)
					})
					.on("mouseleave", function(d) {
						namelabel.text("");
						orglabel.text("");
						dot.style("opacity", 1);
					})

	// Positions the dots based on data.
	function position(dot) {
		dot.attr("cx", function(d) { return Math.min(Math.max(x(d),d.radius),height); })
		   .attr("cy", function(d) { return Math.min(Math.max(y(d),d.radius),height); })
		   .attr("r", function(d) { return Math.min(Math.max( radius(d),0 ),100); }); // this controls the radius of each circle. !currently has no scaling! size is restricted between 0-100
	}

	// Set ball locations and date label
	function setBalls(date) {
		dot.data(interpolateData(date), key).call(position).sort(order);
		  dateLabel.text(parseDate((new Date(date*1000))));
	}

	// interpolate data of the given day
	function interpolateData(date) {
		return projects.map(function(d) {
		  return {
			name: d.name,
			organization: d.organization,
			xAxis: processValues(interpolateValues(d.xAxisActual, date),interpolateValues(d.xAxisPlanned, date)),
			yAxis: processValues(interpolateValues(d.yAxisActual, date),interpolateValues(d.yAxisPlanned, date)),
			radius: interpolateValues(d.radius, date)
		  };
		});
	}
	function processValues(actual,planned) {
	  if(actual > planned && actual/planned !== Infinity) {
	    return ((actual/planned)*100); // to revert the ballmovement *-1 these lines
	  } else if (planned/actual !== -Infinity) {
	    return (-(planned/actual)*100);
	  }
	}
	/*
	this function does mathematical miracles and interpolates the values where the circles will be drawn.
	*/
	function interpolateValues2(values, date) {
		if(values == undefined || date == undefined) {
			//console.log("taas yksi")
			return 0;
		}
		var i = bisect.left(values, date, 0, values.length - 1),
			a = values[i];
		if (i > 0) {
		  var b = values[i - 1],
			  t = (date - a[0]) / (b[0] - a[0]);
		  var planned = a[1] * (1 - t) + b[1] * t
		  var actual = a[2] * (1 - t) + b[2] * t
		  if(actual > planned) {return ((actual/planned)*100); // to revert the ballmovement *-1 these lines
		  } else {return (-(planned/actual)*100)}
		}
		if(a[2] > a[1]) {return ((a[2]/a[1]))*100; // this is the starting values
		} else {return -((a[1]/a[2])*100)}
	  }

	function interpolateValues(values, date) {
		if(values == undefined || date == undefined) {
			//console.log("taas yksi")
			return 0;
		}
		var i = bisect.left(values, date, 0, values.length - 1),
			a = values[i];
		if(a == undefined) {
			return 0;
		} else if(a.length == 0) {
			return 0;
		}
		if (i > 0) {
		  var b = values[i - 1],
			  t = (date - a[0]) / (b[0] - a[0]);
		  return a[1] * (1 - t) + b[1] * t;
		}
		return a[1];
	  }

	  //Timescale under the graph
	var scaleDate = d3.scaleTime()
						.domain([startDate*1000, endDate*1000])
						.range([0, axisLenghtX])
						.clamp(true); //keeps the slider on the scale

	//building the timeScale-slider
	var timeAxis = svg.append("g")
					  .attr("class","slider")
					  .attr("transform", "translate("+margin.right+","+sliderY+")");

	timeAxis.append("line")
			.attr("class", "track")
			.attr("x1", scaleDate.range()[0])
			.attr("x2", scaleDate.range()[1])
			.select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
			.attr("class", "track-overlay")
			.call(d3.drag()
					.on("start drag", function() { //console.log(parseTime(scaleDate.invert(d3.event.x))); //console output to show slider output
		  /*relocates the balls by given date*/    setBalls((scaleDate.invert(d3.event.x)/1000));
					  /*moves the slider handle*/  handle.attr("cx", scaleDate(scaleDate.invert(d3.event.x)));
												 }));

	// Slider handle
	var handle = timeAxis.insert("circle", ".track-overlay")
						  .attr("class", "handle");

	  // The y and x axis are moved in to place
	  svg.append("g")
		 .attr("class", "xAxis")
		 .attr("transform", "translate("+margin.left+","+height / 2+")")
		 .call(d3.axisBottom(scaleX));

	  svg.append("g")
		 .attr("class", "yAxis")
		 .attr("transform", "translate("+width / 2+","+margin.top+")")
		 .call(d3.axisLeft(scaleY));

	// The function compares the radius of circles a and b and
	//then with the sort command aligns the smaller circle in front of the bigger one
	function order(a, b) {
		return radius(b) - radius(a);
	}

}
