$(document).on("click", ".open-modify", function () {
  var field = $(this).data('field');
  var value = $(this).data('value');
  $(".modal-body h3").html("Modify: " + field);
  $(".modal-body h4").html("Current value: " + value);
  document.getElementById("newValue").type = $(this).data('type');
  document.getElementById("newValue").value = $(this).data('value');
});

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


//  To add all organizations to the modify org modal
$(function(){
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

//  To add all persons to the modify per modal
$(function(){
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

$(function(){
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

$(function(){
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

$(function(){
  $(".open-modify-text").click(function(event){
    var field_name = $(this).data('field');
    $("#hidden-text-info").val(field_name);
  });
});
$(function(){
  $(".open-modify-dec").click(function(event){
    var field_name = $(this).data('field');
    $("#hidden-dec-info").val(field_name);
  });
});
$(function(){
  $(".open-modify-per").click(function(event){
    var field_name = $(this).data('field');
    console.log(field_name);
    $("#hidden-per-info").val(field_name);
  });
});
