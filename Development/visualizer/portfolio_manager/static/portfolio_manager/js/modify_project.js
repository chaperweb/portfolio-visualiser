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

//  To submit modify-org-form
$(function()
{
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
  })
});

//  To submit modify-assorg-form
$(function()
{
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
  })
});

//  To submit modify-per-form
$(function()
{
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
  })
});

// To submit modify-dec-form
$(function()
{
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
  })
});

// To submit modify-text-form
$(function()
{
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
  })
});

// To submit modify-date-form
$(function()
{
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
  })
});

//  ############################
//  ### POPULATION FUNCTIONS ###
//  ############################

//  To populate organizationlist in modify_org_modal
$(function()
{
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
});

//  To populate organizationlist in modify_assorg_modal
$(function()
{
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
});

//  To populate personslist in modify_per_modal
$(function()
{
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
});

// To populate associated persons in multiple-items-modal
$(function()
{
  $(".multiple-button").click(function(e){
    // Buttons data variables
    var field = $(this).data('field');
    var projectID = $(this).data('projectid');
    var type = $(this).data('type');

    // Add title
    $("#multiple-title").html(field);

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
      method: "GET",
      url: "/get_multiple/" + projectID + "/" + type + "/" + field,
      data: {},
      success: function(json) {
        $("#multiple-well-ul > li").remove();
        for(i=0; i<json.names.length; i++)
        {
          console.log(json.names[i])
          var row = '<li class="list-group-item">' + json.names[i] + '</li>';
          $(row).appendTo("#multiple-well-ul");
        }
      },
      error: function() {
        alert("Failed to load all persons");
      }
    });
  });
});

//  #############################
//  ### HIDDEN INFO FUNCTIONS ###
//  #############################
// These are to add the hidden field input of all modals that need it

$(function(){
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
