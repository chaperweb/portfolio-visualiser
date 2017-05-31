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
      $("#history-well-ul > li").remove();
      var names = JSON.parse(data);
        // loop for sheet names and urls
      for(i=0;i<names.length;i = i + 2)
      {
        var row = "<li class='list-group-item'><a href='" + names[i+1] + "'>" + names[i] + "</a></li>"
        $(row).appendTo("#history-well-ul");
      }
    },
    error: function() {
      alert("Failed to load sheet history!");
    }
  });
}

function create_org()
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
    method: "POST",
    url: $('#org-form').attr('action'),
    data: {'orgName': $("#orgName").val()},
    success: function(json) {
      // Remove old modal content
      $("#conf-modal-body > h3").remove();
      $("#conf-modal-body > h4").remove();

      // Add new modal content
      var result = "<h3><strong>" + json.result + "</strong></h5>"
      var org = "<h4>Organization created: " + json.orgName + "</h4>"
      $(result).appendTo($("#conf-modal-body"));
      $(org).appendTo($("#conf-modal-body"));
      $("#confirmation-modal").modal('show');
    },
    error: function() {
      alert("Failed to add new organization");
    }
  });
}

function create_person()
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
    method: "POST",
    url: $('#person-form').attr('action'),
    data: {'first': $("#first_name").val(), 'last': $("#last_name").val()},
    success: function(json) {
      // Remove old modal content
      $("#conf-modal-body > h3").remove();
      $("#conf-modal-body > h4").remove();

      // Add new modal content
      var result = "<h3><strong>" + json.result + "</strong></h5>"
      var org = "<h4>Person created: " + json.name + "</h4>"
      $(result).appendTo($("#conf-modal-body"));
      $(org).appendTo($("#conf-modal-body"));
      $("#confirmation-modal").modal('show');
    },
    error: function() {
      alert("Failed to add new person");
    }
  });
}

function upload_sheet()
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
    method: "POST",
    url: $('#sheet-form').attr('action'),
    data: {'name': $("#inputName").val(), 'url': $("#sheetUrl").val()},

    success: function(json) {
      // Remove old modal content
      $("#conf-modal-body > h3").remove();
      $("#conf-modal-body > h4").remove();

      // Add new modal content
      var result_text = "<h3><strong>" + json.result_text + "</strong></h5>"
      var sheet_name = "<h4>Sheetname: " + json.name + "</h4>"

      $(result_text).appendTo($("#conf-modal-body"));
      $(sheet_name).appendTo($("#conf-modal-body"));
      $("#confirmation-modal").modal('show');
      $("#loading").hide();
    },
    error: function() {
      alert("Failed!");
      $("#loading").hide();
    }
  });


}

$(function(){
  // When you click the history button the history-modal opens
  $("#sheetHistory").on("click", function(){
    $("#history-modal").modal('show');
  });
  // Show the history modal and add the content with
  // get_sheet_history
  $("#history-modal").on("show.bs.modal", function(e){
    var modal = $(this);
    get_sheet_history();
  });

  // When you submit the organization form it stops the default
  // behaviour and submit the form with ajax
  $('#org-form').on('submit', function(event){
    event.preventDefault();
    create_org();
  });

  // Same as above for organizations, but for persons this time
  $('#person-form').on('submit', function(event){
    event.preventDefault();
    create_person();
  });


  // Same but for the sheets
  $('#sheet-form').on('submit', function(event){
    event.preventDefault();
     $("#loading").show();
    upload_sheet();
  });
});
