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
    var orgs_html = "<option value="+json[i].name+">"+json[i].name+"</option>";
    $(orgs_html).appendTo($("#associatedorganization-value"));
  }
}
function populate_persons(json) {
  for(i=0;i<json.length;i++) {
    var fullname = json[i].first_name + " " + json[i].last_name
    var option = "<option value= " + json[i].id + ">" + fullname + "</option>";
    $(option).appendTo($("#associatedperson-value"));
  }
}
function ajax_error() {
  alert("Ajax didn't receive a response!");
}


$(function()
{
  //  Add field type to modal when opened
  $(".modify-button").click(function(e) {
    // e.stopPropagation();
    $("#hidden-"+$(this).data('type')+"-info").val($(this).data('field'));

    if ($(this).data('multiple')) {
      // Buttons data variables
      var field = $(this).data('field');
      var projectID = $(this).data('projectid');
      var type = $(this).data('type');

      // Add title
      $("#multiple-title").html(field);

      // Send ajax request to get the items and then populate the list
      $.ajax({
        method: "GET",
        url: "/get_multiple/" + type + "/" + field,
        success: function(json) {
          // Remove old content from the modal
          $("#multiple-well-ul > li").remove();

          // If concerning multiple persons
          if( json.type == "persons" )
          {
            for(i=0; i<json.items.length; i++)
            {
              // ID to be able to remove the row if person removed
              var id = ' id="multiple-person-' + json.items[i].id + '"';
              // Data items for the backend to br able to identify the person
              var data = ' data-name="' + json.items[i].name + '"' + ' data-id="' + json.items[i].id + '"';
              var button = '<button class="btn btn-danger btn-xs pull-right remove-multiple-persons"' + data + '><span class="glyphicon glyphicon-remove"></span></button>'
              // Create the list item and add the row to the modal
              var row = '<li' + id + 'class="list-group-item">' + json.items[i].name + button + '</li>';
              $(row).appendTo("#multiple-well-ul");
            }
            var addLabel = '<label for="add-person-to-project" class="pull-left">Add person</label>';
            var addSelect = '<select id="add-person-to-project" name="perID"></select>';
            var addBtn = '<button class="btn btn-orange btn-xs pull-right"><span class="glyphicon glyphicon-plus"></span></button>';
            var addlist = '<li class="list-group-item"><form action="/add_person_to_project" method="POST" id="add-person-to-project-form">' + addLabel + addSelect + addBtn + '</form></li>';
            $(addlist).appendTo("#multiple-well-ul");
            $.ajax({
              method: "GET",
              url: "/get_pers",
              data: {},
              success: function(json) {
                for(i=0;i<json.length;i++)
                {
                  var fullname = json[i].first_name + " " + json[i].last_name
                  var option = "<option value= " + json[i].id + ">" + fullname + "</option>";
                  $(option).appendTo($("#add-person-to-project"));
                }
              },
              error: function() {
                alert("Failed to load all persons");
              }
            });
          }
          // If concerning multiple projects
          else if( json.type == "projects" )
          {
            for(i=0; i<json.items.length; i++)
            {
              // Look above for explanations
              var id = ' id="multiple-project-' + json.items[i].id + '"';
              var data = ' data-name="' + json.items[i].name + '"' + ' data-id="' + json.items[i].id + '"';
              var button = '<button class="btn btn-danger btn-xs pull-right remove-multiple-projects"' + data + '><span class="glyphicon glyphicon-remove"></span></button>'
              var row = '<li' + id + 'class="list-group-item">' + json.items[i].name + button + '</li>';
              $(row).appendTo("#multiple-well-ul");
            }
            var addLabel = '<label for="add-project-to-project" class="pull-left">Add project</label>';
            var addSelect = '<select id="add-project-to-project" name="projID"></select>';
            var addBtn = '<button class="btn btn-orange btn-xs pull-right"><span class="glyphicon glyphicon-plus"></span></button>';
            var addlist = '<li class="list-group-item"><form action="/add_project_to_project" method="POST" id="add-project-to-project-form">' + addLabel + addSelect + addBtn + '</form></li>';
            $(addlist).appendTo("#multiple-well-ul");
            $.ajax({
              method: "GET",
              url: "/get_proj",
              data: {},
              success: function(json) {
                for(i=0;i<json.length;i++)
                {
                  var option = "<option value= " + json[i].id + ">" + json[i].name + "</option>";
                  $(option).appendTo($("#add-project-to-project"));
                }
              },
              error: function() {
                alert("Failed to load all projects");
              }
            });
          }

          // If the add person form is submitted
          $("#add-person-to-project-form").on("submit", function(e)
          {
            e.preventDefault();
            $.ajax({
              method: "POST",
              url: $('#add-person-to-project-form').attr('action'),
              data: { 'projectID': projectID, 'personID': $("#add-person-to-project").val() },
              success: function(json) {
                // TODO: Don't alert, just add it to the list
                alert("Successfully added " + json.name + " to " + field);
                $("#multiple-items-modal").modal('hide');
              },
              error: function() {
                alert("Failed to add person to " + field);
              }
            });
          });

          // If the add project form is submitted
          $("#add-project-to-project-form").on("submit", function(e)
          {
            e.preventDefault();
            $.ajax({
              method: "POST",
              url: $('#add-project-to-project-form').attr('action'),
              data: { 'destID': projectID, 'toBeAddedID': $("#add-project-to-project").val() },
              success: function(json) {
                // TODO: Don't alert, just add it to the list
                alert("Successfully added " + json.name + " to " + field);
                $("#multiple-items-modal").modal('hide');
              },
              error: function() {
                alert("Failed to add project to " + field);
              }
            });
          });

          // If a remove button for a person is clicked
          // Sends an ajax request to remove the person from the project
          $(".remove-multiple-persons").click(function(e)
          {
            $.ajax({
              method: "PATCH",
              url: "/remove_person_from_project",
              data: { 'id': $(this).data('id'), 'project_id': projectID },
              success: function(json) {
                // Remove the row that contained the removed person
                $("#multiple-person-" + json.id).remove()
              },
              error: function() {
                alert("Failed to remove person from project");
              }
            });
          });

          // Sends ajax request to remove the associated project
          $(".remove-multiple-projects").click(function(e)
          {
            $.ajax({
              method: "PATCH",
              url: "/remove_project_from_project",
              data: { 'id': $(this).data('id'), 'project_id': projectID },
              success: function(json) {
                // Remove the row that contained the removed person
                $("#multiple-project-" + json.id).remove()
              },
              error: function() {
                alert("Failed to remove project from project");
              }
            });
          });
        },
        error: function() {
          alert("Failed to load")
        }
      });
      console.log("MULTIPLE MODIFY CLICKED!");
    }

    // OPEN MODAL
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

  // To populate the list in multiple-items-modal
  $(".multiple-button").click(function(e){
    // Buttons data variables
    var field = $(this).data('field');
    var projectID = $(this).data('projectid');
    var type = $(this).data('type');

    // Add title
    $("#multiple-title").html(field);

    // Send ajax request to get the items and then populate the list
    $.ajax({
      method: "GET",
      url: "/get_multiple/" + projectID + "/" + type + "/" + field,
      data: {},
      success: function(json) {
        $("#multiple-well-ul > li").remove();
        if( json.type == "persons" )
        {
          for(i=0; i<json.items.length; i++)
          {
            var row = '<li class="list-group-item">' + json.items[i].name + '</li>';
            $(row).appendTo("#multiple-well-ul");
          }
        }
        else if( json.type == "projects" )
        {
          for(i=0; i<json.items.length; i++)
          {
            var row = '<li class="list-group-item">' + json.items[i].name + '</li>';
            $(row).appendTo("#multiple-well-ul");
          }
        }
      },
      error: function() {
        alert("Failed to load")
      }
    });
  });

});
