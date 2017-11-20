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

//var db_json;

function fourField(json, target, xToBe, yToBe, radToBe, startDate, endDate, sliderValues, sliderDate) {
	// console.log(json);
	var projects = [],

	colorToBe = 'AssociatedOrganizationDimension',
	// size of the display box and other scaling related variables
	sliderHeight = 50,
	fieldWidth =Math.max(600,($("#" + target).height() - sliderHeight)),
	svgHeight = fieldWidth + sliderHeight,
	margin = {right: fieldWidth * 0.05, left: fieldWidth * 0.05, top: fieldWidth * 0.05, bottom: sliderHeight},
	axisLengthX = fieldWidth * 0.9,
	axisLengthY = fieldWidth * 0.9,
	sliderY = fieldWidth,
	percentInPx = (axisLengthX / (2*sliderValues)) * 100,
	// variables for default dates
	startDefault = 0,
	endDefault = 0;

	var radiusArray = [];

	// The scales for the x and y axis.
	// range means the length of the line and domain the numbers beneath it
	var scaleX = d3.scaleLinear()
									.range([0,axisLengthX])
									.domain([-1 * sliderValues, sliderValues]);

	var scaleY = d3.scaleLinear()
									.range([0,axisLengthY])
									.domain([sliderValues,-1 * sliderValues]);

	//list for the organizations
	var organizations = [];
	var size;

	for (j = 0; j < json.length; j++) {
		size = json[j].dimensions.length;
		/*inProgress is object which will contain the data from 1 project.
		name, organization,
		x-axis values from input data, x-axis values from milestones
		radius values
		y-axis values from input data, y-axis values from milestones
		first date of this project, last date of this project
		dates are defaulted to infinity so the math.min/max can operate them as numbers
		*/
		var inProgress = {
			"name": json[j].name,
			"organization": "",
			"xAxisActual": [],
			"xAxisPlanned": [],
			"radius": [],
			"yAxisActual": [],
			"yAxisPlanned": [],
			"firstDate": Infinity,
			"lastDate": -Infinity
		};
		var dimension,
		collectVal,
		valueName,
		historyList,
		date,
		planned,
		parsedDate,
		valueName;

		var xID = 0,
		yID = 0;

		for (i = 0; i < size; i++) {
			dimension = json[j].dimensions[i];
			if (dimension.dimension_type == 'NumberDimension' ) {
				// collectVal is array which will contain a value and a corresponding
				// date. The type of the values is determined later (budget, manHours etc.).
				collectVal = [];
				historyList = dimension.dimension_object.history;
				historyLen = historyList.length;
				for (h = 0; h < historyLen; h++) {
					date = historyList[h].history_date;
					planned = historyList[h].value;
					// parsing date to timestamp. It is divided by 1000 since JS timestamp is in milliseconds.
					parsedDate = new Date(date).getTime() / 1000;
					inProgress.firstDate = Math.min(parsedDate, inProgress.firstDate);
					inProgress.lastDate = Math.max(parsedDate, inProgress.lastDate);
					setDateScale(parsedDate);
					collectVal.push([parsedDate, planned]);
				};
				// here we determine the type of the array, set the inProgress arrays.
				valueName = dimension.dimension_object.name;
				if ( valueName === xToBe) {
					xID = dimension.id // x-axis id is saved. This value is used in the milestone-loop.
					inProgress.xAxisActual = (collectVal).reverse();
				} else if (valueName === yToBe) {
					yID = dimension.id // y-axis id is saved. This value is used in the milestone-loop.
					inProgress.yAxisActual = (collectVal).reverse();
				} else if (valueName === radToBe) {
					inProgress.radius = (collectVal).reverse();
					radiusArray.push.apply(radiusArray,collectVal);
				};
			} else if (dimension.dimension_type === colorToBe ) {
				if(dimension.dimension_object.history[0].value) {
					inProgress.organization = dimension.dimension_object.history[0].value.name;
				} else {
					//project has no organization
					inProgress.organization = "";
				};
				organizations.push(inProgress.organization);
			};

		};
		var milestone;
		const dayInSeconds = 86400;

		//The milestonarrays are initialized here. both arrays will have 1 value set by
		//default to improve interpolation between the actual start and the first milestone.
		var collectXPlan = [(inProgress.firstDate - dayInSeconds, 0)],
		collectYPlan = [(inProgress.firstDate - dayInSeconds, 0)];

		if(json[j].milestones != undefined) {
			for(e = 0; e < json[j].milestones.length ; e++ ) {
				milestone = json[j].milestones[e];
				if(milestone.dimensions != undefined) {
					for(q = 0; q < milestone.dimensions.length ; q++ ) {
						if(milestone.dimensions[q].project_dimension == xID) {	// ADD X
							date = milestone.due_date;
							parsedDate = new Date(date).getTime() / 1000;
							milestoneValue = milestone.dimensions[q].dimension_milestone_object.value;
							collectXPlan.push([parsedDate,milestoneValue]);
						} else if( milestone.dimensions[q].project_dimension == yID ) {	// ADD Y
							date = milestone.due_date;
							parsedDate = new Date(date).getTime() / 1000;
							milestoneValue = milestone.dimensions[q].dimension_milestone_object.value;
							collectYPlan.push([parsedDate,milestoneValue]);
						};
						inProgress.firstDate = Math.min(parsedDate, inProgress.firstDate);
						inProgress.lastDate = Math.max(parsedDate, inProgress.lastDate);
						setDateScale(parsedDate);
					};
				};
			};
			//pushing the milestone-arrays to inProgress, and push inProgress to projects-array.
			inProgress.xAxisPlanned = (collectXPlan);
			inProgress.yAxisPlanned = (collectYPlan);
			projects.push(inProgress);
		};
	};
	var maxRadius = 0;
	var minRadius = Infinity;
	var parsedNumber;

	//getting min and max values for the radius-values
	radiusArray.forEach(function(d) {
		parsedNumber = parseInt(d[1]);
		if(parsedNumber < minRadius) {
			minRadius = parsedNumber;
		}
		if(parsedNumber > maxRadius) {
			maxRadius = parsedNumber;
		};
	});

	var uniqueOrganizations = organizations.filter( onlyUnique );

	var fourFieldColors = enoughColors(uniqueOrganizations.length, colors);

	//creating colorscale for the visualization
	var colorScale = d3.scaleOrdinal()
											.domain(uniqueOrganizations)
											.range(fourFieldColors);
	//creating linearscale to scale the balls
	var linearScale = d3.scaleLinear()
											.domain([minRadius,maxRadius])
											.range([5,100])
											.clamp(true);

	ddmmyy = d3.timeFormat("%d/%m/%Y");

	if (isNaN(startDate)) {
		startDate = startDefault;
		$('#start-date-selector').val(ddmmyy(startDate*1000));
	}
	if(isNaN(endDate)) {
		endDate = endDefault;
		$('#end-date-selector').val(ddmmyy(endDate*1000));
	};
	if (isNaN(sliderDate)) {
		sliderDate = startDate;
	} else if(sliderDate < startDate) {
		sliderDate = startDate;
	} else if(sliderDate > endDate) {
		sliderDate = endDate;
	};

	//console.log(projects);

	/***********************/
	/* functions live here */
	/***********************/

	//function to determine the x-coordinate of a circle in the graph.
	function x(d) {
		return margin.left + (sliderValues/100 + d.xAxis) * percentInPx;
	};
	//function to determine the y-coordinate of a circle in the graph.
	function y(d) {
		return margin.top + (sliderValues/100 + d.yAxis) * percentInPx;
	};
	/*function to determine the radius of a circle in the graph.
	*If given location is not valid, the radius is set to 0, and the circle is not displayed
	*/
	function radius(d) {
		if (validLocation(d)) {
			return d.radius;
		} else {
			d.radius = 0;
			return d.radius;
		};
	};
	//This function is for the filter to rule out not unique values from array
	function onlyUnique(value, index, self) {
		return self.indexOf(value) === index;
	};
	/*
	* Helps to set timescale-slider by min&max values of
	* given data points and milestones
	*/
	function setDateScale(date) {
		if (startDefault == 0 && endDefault == 0) {
			startDefault = date;
			endDefault = date;
			return;
		};
		if (date > endDefault) {
			endDefault = date;
		} else if (date < startDefault) {
			startDefault = date;
		};
	};

	/* If
	* 1) y- or x-coordinates are infinite (the ball lacks milestones or dimension values)
	* or
	* 2) Ball location is outside of given axis
	* the calculated location will not be valid
	*/
	function validLocation(d) {
		return (
			d.yAxis !== -Infinity &&
			d.yAxis !== Infinity &&
			d.xAxis !== Infinity &&
			d.xAxis !== -Infinity &&
			y(d) > linearScale(d.radius)  &&
			x(d) > linearScale(d.radius) &&
			y(d) < (margin.top + axisLengthY + margin.bottom - linearScale(d.radius)) &&
			x(d) < (margin.left + axisLengthX + margin.right - linearScale(d.radius)));
		};
		function validXCoordinates(d) {
			if(!isNaN(d)) {return Math.min(Math.max(d,0),fieldWidth) } else {return 0};
		};
		function validYCoordinates(d) {
			if(!isNaN(d)) {return Math.min(Math.max(d,0),fieldWidth) } else {return 0};
		};

		//function to determine color of the circle. Currently is set to color the circles by their "AssociatedOrganizationDimension"
		function color(d) { return colorScale(d.organization); };
		function key(d) { return d.name; };

		// Positions the dots based on data, the only scaling happens here as the ball max r is limited to 100
		function position(dot) {
			dot.attr("cx", function(d) { return validXCoordinates(x(d)) ; })
			.attr("cy", function(d) { return validYCoordinates(y(d)); })
			.attr("r", function(d) {
				if(radius(d) <= 0) {
					return 0;
				} else {
					return linearScale(radius(d));
				};
			});
		};

		// Set ball locations and date label value
		function setBalls(date) {
			dot.data(interpolateData(date), key).call(position).sort(order);
			dateLabel.text(parseDate((new Date(date*1000))));
		};

		// interpolate data of the given day
		function interpolateData(date) {
			return projects.map(function(d) {
				return {
					name: d.name,
					organization: d.organization,
					xAxis: processValues(interpolateValues(d, d.xAxisActual, date),interpolateValues(d, d.xAxisPlanned, date)),
					yAxis: processValues(interpolateValues(d, d.yAxisActual, date),interpolateValues(d, d.yAxisPlanned, date)),
					radius: interpolateValues(d, d.radius, date)
				};
			});
		};
		// this function returns the required % in decimal form to position the circle correctly.
		function processValues(actual,planned) {
			return ( ((actual/planned) -1));
		};

		/*
		this function interpolates the values of the given array "values",
		and returns the value that is in the date "date".
		is used in interpolateData-function.
		*/
		function interpolateValues(dot, values, date) {
			if (values == undefined || date == undefined || date < dot.firstDate || date > dot.lastDate) {
				//array containing the data is undefined, most likely the data never existed.
				//The value will be eventyally set to 0.
				return 0;
			};
			var i = bisect.left(values, date, 0, values.length - 1),
			a = values[i];
			if (a == undefined) {
				return 0;
			} else if(a.length == 0) {
				return 0;
			};
			if (i > 0) {
				var b = values[i - 1],
				t = (date - a[0]) / (b[0] - a[0]);
				return a[1] * (1 - t) + b[1] * t;
			};
			return a[1];
		};
		//Bisector for interpolation
		var bisect = d3.bisector(function(d) { return d[0]; });

		// The function compares the radius of circles a and b and
		//then with the sort command aligns the smaller circle in front of the bigger one
		function order(a, b) {
			return radius(b) - radius(a);
		};
		/*********************************/
		/* Graph elements live down here */
		/*********************************/

		//container for everything

		var svg = d3.select("#" + target).append("svg")
					.attr("width", fieldWidth)
					.attr("height", svgHeight);


		//Parser for a human readable date format dd. mm. yyyy
		var parseDate = d3.timeFormat("%d. %m. %Y");

		// Add the date label; the value is set on transition.
		var dateLabel =  svg.append("text")
												.attr("class", "currentDate")
												.attr("text-anchor", "end")
												.attr("y", svgHeight - 100)
												.attr("x", fieldWidth )
												.text(parseDate((new Date(startDate*1000))));

		//slider start & stop values
		var labelStart = parseDate(startDate * 1000);
		var labelEnd = parseDate(endDate * 1000);
		//label for the start date next to the slider
		var sSLabel = svg.append("text")
											.attr("class", "sliderLabel")
											.attr("text-anchor", "start")
											.attr("x", 0)
											.attr("y", svgHeight)
											.text("Start date: " + labelStart);

		//label for the end date next to the slider
		var sELabel = svg.append("text")
											.attr("class", "sliderLabel")
											.attr("text-anchor", "end")
											.attr("x", fieldWidth)
											.attr("y", svgHeight)
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
										.text("x-axis: "+xToBe);
		//label for y-axis
		var ylabel = svg.append("text")
										.attr("class", "axisLabel")
										.attr("text-anchor", "start")
										.attr("y", 340)
										.attr("x", 20)
										.text("y-axis: "+yToBe);

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
										dot.style("opacity", .4);
										d3.select(this).style("opacity", 1);
										d3.selectAll(".selected").style("opacity", 1);
									})
									.on("mouseleave", function(d) {
										namelabel.text("");
										orglabel.text("");
										dot.style("opacity", 1);
									});

		//Timescale under the graph
		var scaleDate = d3.scaleTime()
											.domain([startDate*1000, endDate*1000])
											.range([0, axisLengthX])
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
						.on("start drag", function() {
							setBalls((scaleDate.invert(d3.event.x)/1000)); /*relocates the balls by given date*/
							handle.attr("cx", scaleDate(scaleDate.invert(d3.event.x))); /*moves the slider handle*/
						}));

		// Slider handle
		var handle = timeAxis.insert("circle", ".track-overlay")
													.attr("class", "handle")
													.attr("r", 20)
													.attr("cx", scaleDate(sliderDate));
													// The y and x axis are moved in to place
													svg.append("g")
													.attr("class", "xAxis")
													.attr("transform", "translate("+margin.left+","+(fieldWidth / 2)+")")
													.call(d3.axisBottom(scaleX));

		svg.append("g")
				.attr("class", "yAxis")
				.attr("transform", "translate("+fieldWidth / 2+","+margin.top+")")
				.call(d3.axisLeft(scaleY));

		//if the user zoomed the image, the timescale does not reset
		setBalls(sliderDate);
		svg.select(".handle").node().cx.baseVal.value = scaleDate(sliderDate * 1000);
		return svg;
};
