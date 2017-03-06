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

function get_sheet_history()
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
    url: $('#sheetHistory').data('sheeturl'),
    data: {},
    success: function(data) {
      alert("Successfully saved score!");
      alert(data);
    },
    error: function() {
      error("Score could not be submitted!");
    }
  });
}


$(function(){
  // When you clik the history button the history-modal opens
  $("#sheetHistory").on("click", function(){
    $("#history-modal").modal('show');
  });

  $("#history-modal").on("show.bs.modal", function(e){
    var modal = $(this);
    get_sheet_history();
  });

});
