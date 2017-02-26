var height = 500,
    width = 1000,
    marginY = 200,
    marginX = 100;
    timeY = height+50;

var svg = d3.select("body")
            .append("svg")
            .attr("height", height+marginY)
            .attr("width", width+marginX)
            .append("g")
            .attr("transform", "translate("+50+","+50+")");

var pathData = [{"date": "01-05-16", "budget": 150.10, "owner": "Teuvo"},
                {"date": "15-05-16", "budget": 170.10, "owner": "Teppo"},
                {"date": "01-06-16", "budget": 50.03, "owner": "Matti"},
                {"date": "01-07-16", "budget": 200.04, "owner": "Teppo"}];

//var root = d3.hierarchy(pathData,funcion(d){return d.updates});

//d3.csv("http://ec2-52-213-73-4.eu-west-1.compute.amazonaws.com:8000/data.csv", function(error, pathData){

var parseTime = d3.timeParse("%d-%m-%y");

var x = d3.scaleLinear().range([0,width]),
    y = d3.scaleLinear().range([height,0]);
    z = d3.scaleLinear().range([0,width]);

x.domain([0, (pathData.length-1)]);
y.domain([0, d3.max(pathData, function(d) {
  return d.budget;
})]);
z.domain([0, (pathData.length-1)]);

var valueLine = d3.line()
                    .curve(d3.curveStepAfter)
                    .x( function(d,i) {
                      return x(i);
                    })
                    .y( function(d) {
                      return y(d.budget);
                    });

svg.append("path")
    .attr("class", "line")
    .attr("d", valueLine(pathData));

svg.append("g")
   .attr("transform", "translate(0,"+height+")")
   .call(d3.axisBottom(x).ticks(pathData.length))
   .selectAll("text")
   .data(pathData)
   .text( function(d) {
     return d.owner;
   });

svg.append("g")
   .call(d3.axisLeft(y));

svg.append("g")
  .attr("transform", "translate(0,"+timeY+")")
  .call(d3.axisBottom(z).ticks(pathData.length))
  .selectAll("text")
  .data(pathData)
  .text( function(d) {
    return d.date;
  });

d3.select("body")
  .append("ul")
  .text("Updates")
  .selectAll("li")
  .data(pathData)
  .enter()
  .append("li")
  .text( function(d) {
    return d.date;
  });

//});