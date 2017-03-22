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

//  #######################################
//  ### PREVENTING AUTOMATIC EXPANSIONS ###
//  #######################################
$(function()
{
  $(".modify-button").click(function(e) {
    e.preventDefault();
    e.stopPropagation();
    var modalId = $(this).data('target');
    $(modalId).modal('toggle');
  });
})

//  ############################
//  ### SUBMITTING FUNCTIONS ###
//  ############################
$(function()
{
  //  To submit modify-org-form
  $("#modify-org-form").on("submit", function(event)
  {
    event.preventDefault();

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
    $.ajax({
      method: "POST",
      url: $('#modify-org-form').attr('action'),
      data: { 'name': $("#newOrg").val() },
      success: function(json) {
        $("#projectparent").text(json.name);
        $("#modify-org-modal").modal('hide');
      },
      error: function() {
        alert("Failed to modify organization");
      }
    });
  });

  //  To submit modify-assorg-form
  $("#modify-assorg-form").on("submit", function(event)
  {
    event.preventDefault();

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

    $.ajax({
      method: "POST",
      url: $('#modify-assorg-form').attr('action'),
      data: { 'org': $("#org").val(), 'field': $("#hidden-assorg-info").val() },
      success: function(json) {
        var textToChange = "#" + json.field
        $(textToChange).text(json.value);
        $("#modify-assorg-modal").modal('hide');
      },
      error: function() {
        alert("Failed to modify organization");
      }
    });
  });

  //  To submit modify-per-form
  $("#modify-per-form").on("submit", function(event)
  {
    event.preventDefault();

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
    $.ajax({
      method: "POST",
      url: $('#modify-per-form').attr('action'),
      data: { 'perID': $("#person").val(), 'field': $("#hidden-per-info").val() },
      success: function(json) {
        var textToChange = "#" + json.field
        $(textToChange).text(json.value);
        $("#modify-per-modal").modal('hide');
      },
      error: function() {
        alert("Failed to modify organization");
      }
    });
  });

  // To submit modify-dec-form
  $("#modify-dec-form").on("submit", function(event)
  {
    event.preventDefault();

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
    $.ajax({
      method: "POST",
      url: $('#modify-dec-form').attr('action'),
      data: { 'decValue': $("#newDecValue").val(),
              'field': $("#hidden-dec-info").val()
            },
      success: function(json) {
        var textToChange = "#" + json.field
        $(textToChange).text(json.value);
        $("#modify-dec-modal").modal('hide');
      },
      error: function() {
        $("#modify-dec-modal").modal('hide');
        alert("Failed to modify decimal field");
      }
    });
  });

  // To submit modify-text-form
  $("#modify-text-form").on("submit", function(event)
  {
    event.preventDefault();

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
    $.ajax({
      method: "POST",
      url: $('#modify-text-form').attr('action'),
      data: { 'textValue': $("#newTextValue").val(),
              'field': $("#hidden-text-info").val()
            },
      success: function(json) {
        var textToChange = "#" + json.field
        $(textToChange).text(json.value);
        $("#modify-text-modal").modal('hide');
      },
      error: function() {
        $("#modify-text-modal").modal('hide');
        alert("Failed to modify text field");
      }
    });
  });

  // To submit modify-date-form
  $("#modify-date-form").on("submit", function(event)
  {
    event.preventDefault();

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

    $.ajax({
      method: "POST",
      url: $('#modify-date-form').attr('action'),
      data: { 'date': $("#date").val(),
              'field': $("#hidden-date-info").val()
            },
      success: function(json) {
        var textToChange = "#" + json.field
        $(textToChange).text(json.value);
        $("#modify-date-modal").modal('hide');
      },
      error: function() {
        $("#modify-date-modal").modal('hide');
        alert("Failed to modify date field");
      }
    });
  });
});

//  ############################
//  #### REMOVING FUNCTIONS ####
//  ############################



//  ############################
//  ### POPULATION FUNCTIONS ###
//  ############################
$(function()
{
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

  //  To populate organizationlist in modify_org_modal
  $.ajax({
    method: "GET",
    url: "/get_orgs",
    data: {},
    success: function(json) {
      for(i=0;i<json.length;i++)
      {
        var option = "<option value= " + json[i].name + ">";
        $(option).appendTo($("#organizations"));
      }
    },
    error: function() {
      alert("Failed to load all organizations");
    }
  });

  //  To populate organizationlist in modify_assorg_modal
  $.ajax({
    method: "GET",
    url: "/get_orgs",
    data: {},
    success: function(json) {
      for(i=0;i<json.length;i++)
      {
        var option = "<option value= " + json[i].name + ">" + json[i].name + "</option>";
        $(option).appendTo($("#org"));
      }
    },
    error: function() {
      alert("Failed to load all organizations");
    }
  });

  //  To populate personslist in modify_per_modal
  $.ajax({
    method: "GET",
    url: "/get_pers",
    data: {},
    success: function(json) {
      for(i=0;i<json.length;i++)
      {
        var fullname = json[i].first_name + " " + json[i].last_name
        var option = "<option value= " + json[i].id + ">" + fullname + "</option>";
        $(option).appendTo($("#person"));
      }
    },
    error: function() {
      alert("Failed to load all persons");
    }
  });

  // To populate the list in multiple-items-modal
  $(".multiple-button").click(function(e){
    // Buttons data variables
    var field = $(this).data('field');
    var projectID = $(this).data('projectid');
    var type = $(this).data('type');
    console.log("field: " + field + "\nID: " + projectID + "\ntype: " + type);

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

  // To populate the list in multiple-items-modal when modify button is clicked
  $(".multiple-modify-button").click(function(e){
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
        }

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
  });
});

//  #############################
//  ### HIDDEN INFO FUNCTIONS ###
//  #############################
// These are to add the hidden field input of all modals that need it
$(function()
{
  //  Adding text field info
  $(".open-modify-text").click(function(event){
    var field_name = $(this).data('field');
    $("#hidden-text-info").val(field_name);
  });
  //  Adding decimal field info
  $(".open-modify-dec").click(function(event){
    var field_name = $(this).data('field');
    $("#hidden-dec-info").val(field_name);
  });
  //  Adding person field info
  $(".open-modify-per").click(function(event){
    var field_name = $(this).data('field');
    $("#hidden-per-info").val(field_name);
  });
  //  Adding date field info
  $(".open-modify-date").click(function(event){
    var field_name = $(this).data('field');
    $("#hidden-date-info").val(field_name);
  });
  //  Adding assorg field info
  $(".open-modify-assorg").click(function(event){
    var field_name = $(this).data('field');
    $("#hidden-assorg-info").val(field_name);
  });
});
