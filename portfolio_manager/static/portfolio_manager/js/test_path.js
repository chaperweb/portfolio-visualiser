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
		  				"dimension_type": "DecimalDimension"
	  				};
  path_data = path.generate_path_data(x_dim, y_dim)
  assert.equal( '2014-12-25T00:00:00Z' , path_data[0].history_date, 'Date of first data point is '+path_data[0].history_date ) ;
  assert.equal( '2015-06-06T00:00:00Z' , path_data[1].history_date, 'Date of second data point is '+path_data[1].history_date ) ;
  assert.equal( '2015-07-05T00:00:00Z' , path_data[2].history_date, 'Date of third data point is '+path_data[2].history_date ) ;
  assert.equal( 3 , path_data.length, 'Path data contains three data points.' ) ;
  assert.end() ;
} ) ;

