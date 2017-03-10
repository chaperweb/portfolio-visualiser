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

$(function(){
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
        alert("Failed to add new organization");
      }
    });
  })
});

$(function(){
  $(".open-modify-text").click(function(event){
    var field_name = $(this).data('field');
    $("#hidden-text-info").val(field_name);
  });
})
