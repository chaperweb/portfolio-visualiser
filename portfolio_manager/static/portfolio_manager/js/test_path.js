var tape_test = require( 'tape' ) ;
var path = require( './path.js' ) ;

tape_test( 'Test generate_path_data history_date parsing', function( assert ) {

	x_dim = {	"id": 1,
		  				"dimension_object":
		  					{
		  						"name": "Name",
		  						"history": [
		  							{	"id": 1,
		  								"value": "Project1",
		  								"history_date": "2014-12-25T00:00:00Z",
		  								"string": "Project1"
		  							}
		  						]
		  					},
		  				"dimension_type": "TextDimension"
	  				};
	y_dim = {	"id": 2,
		  				"dimension_object":
		  					{
		  						"name": "Money",
		  						"history": [
		  							{	"id": 3,
		  								"value": "2",
		  								"history_date": "2015-07-05T00:00:00Z",
		  								"string": "2"
		  							},
		  							{	"id": 2,
		  								"value": "1",
		  								"history_date": "2015-06-06T00:00:00Z",
		  								"string": "1"
		  							}
		  						]
		  					},
		  				"dimension_type": "NumberDimension"
	  				};
  path_data = path.generate_path_data(x_dim, y_dim)
  assert.equal( '2014-12-25T00:00:00Z' , path_data[0].history_date, 'Date of first data point is '+path_data[0].history_date ) ;
  assert.equal( '2015-06-06T00:00:00Z' , path_data[1].history_date, 'Date of second data point is '+path_data[1].history_date ) ;
  assert.equal( '2015-07-05T00:00:00Z' , path_data[2].history_date, 'Date of third data point is '+path_data[2].history_date ) ;
  assert.equal( 3 , path_data.length, 'Path data contains three data points.' ) ;
  assert.end() ;
} ) ;
