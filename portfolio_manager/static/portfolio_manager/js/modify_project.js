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

//  COOOOOOOKIES
function getCookie(name)
{
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
      var cookies = document.cookie.split(";");
      for(i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + "=")) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
// Cookies and csrf
var csrftoken = getCookie("csrftoken");
function csrfSafeMethod(method)
{
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  }
});


function populate_organizations(json) {
  for(i=0;i<json.length;i++) {
    var orgs_html = "<option value='"+json[i].id+"'>"+json[i].name+"</option>";
    $(orgs_html).appendTo($("#associatedorganization-value"));
  }
  $("#associatedorganization-value").trigger("chosen:updated")
}
function populate_persons(json) {
  for(i=0;i<json.length;i++) {
    var fullname = json[i].first_name + " " + json[i].last_name
    var option = "<option value='" + json[i].id + "'>" + fullname + "</option>";

    $(option).appendTo($("#associatedperson-value"));
    $(option).appendTo($("#associatedpersons-value"));
  }
  $("#associatedperson-value").trigger("chosen:updated");
  $("#associatedpersons-value").trigger("chosen:updated")
}
function populate_projects(json) {
  for(i=0;i<json.length;i++)
  {
    var option = "<option value='" + json[i].id + "'>" + json[i].name + "</option>";
    $(option).appendTo($("#associatedprojects-value"));
  }
  $("#associatedprojects-value").trigger("chosen:updated")
}
function ajax_error() {
  alert("Ajax didn't receive a response!");
}

function add_multiple_row(name, id, type, field, projectID) {
  var list_id = ' id="multiple-' + type + '-' + id + '"',
      csrf = '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrftoken + '"/>',
      field = '<input type="hidden" name="field" value="' + field + '"/>',
      value = '<input type="hidden" name="value" value="' + id + '"/>',
      url = '"/projects/' + projectID + '/edit/' + type + '"',
      form = '<form method="PATCH" action=' + url + '>' + csrf + field + value,
      button_class = 'class="btn btn-danger btn-xs pull-right"',
      remove_span = '<span class="glyphicon glyphicon-remove"></span>',
      button = '<button type="submit" ' + button_class + '>' + remove_span + '</button>',
      row_class = ' class="list-group-item multiple-row"'
      row = '<li' + list_id + row_class + '>' + form + name + button + '</form></li>';
  $(row).appendTo("#" + type + "-well-ul");
}


$(function()
{
  $('#projects-button').click(function(){
    $('#projects-dropdown').animate({
      height: 'toggle'
    });
  });

  //  Add field type to modal when opened
  $(".modify-button").click(function(e) {
    e.stopPropagation();  // Stop panelbody from opening

    //  Add info about which field we are handling
    var field = $(this).data('field');
    if(field == '') {   // Field has no projectdimension
      $("li.multiple-row").remove();
      $("#hidden-"+$(this).data('type')+"-info").val($(this).attr('id').replace('-modifybtn', ''));
      //field = $(this).attr('id').replace('-modifybtn', '');
    } else {
      $("#hidden-"+$(this).data('type')+"-info").val(field);

      var valuetype = $(this).data('valuetype');
      // If the field is a multiple-field
      if (valuetype == 'multiple') {
        // Buttons data variables
        var projectID = $(this).data('projectid');
        var type = $(this).data('type');
        console.log("/get_multiple/" + type + "/" + field)

        // Send ajax request to get the items and then populate the list
        $.ajax({
          method: "GET",
          url: "/get_multiple/" + type + "/" + field,
          success: function(json) {
            // Remove old content from the modal
            $("li.multiple-row").remove();

            // Add a row for each item in data
            for(i=0; i<json.data.length; i++) {
              var name = json.data[i].name,
                  itemId = json.data[i].id;
              add_multiple_row(name, itemId, json.type, field, projectID);
            }
          },
          error: function() { ajax_error(); }
        });
      }
    }
    // Open the modal
    $("#" + type + "-value").trigger("chosen:updated");
    $($(this).data('target')).modal('toggle');
  });

  //  To populate organizationlists
  $.ajax({
    method: "GET",
    url: "/get_orgs",
    success: function(json) { populate_organizations(json); },
    error: function() { ajax_error(); }
  });

  //  To populate personslists
  $.ajax({
    method: "GET",
    url: "/get_pers",
    success: function(json) { populate_persons(json); },
    error: function() { ajax_error(); }
  });

  //  To populate projectlists
  $.ajax({
    method: "GET",
    url: "/get_proj",
    success: function(json) { populate_projects(json); },
    error: function() { ajax_error(); }
  });
});
$(function() {
  $("select").each(function(){
    $(this).chosen({width:'50%'});
  })
});
