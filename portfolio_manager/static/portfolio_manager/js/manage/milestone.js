$.fn.refresh = function() {
    return $(this.selector);
};

function checkRows(pid) {
  var inputs = $('.new-mile-field-' + pid),
    errorFree = true;

  inputs.each(function() {
    errorFree = errorFree && ($(this).val() != '');
  });

  return errorFree;
}

function submitRow(pid) {
  console.log("THIS SHOULD SUBMIT FORM#" + pid);
}

function inputsToCells(pid) {
  var inputs = $(".new-mile-field-" + pid);
  inputs.each(function() {
    if ($(this)[0].type == 'date') {  // Date needs to be formatted
      var dateparts = $(this).val().split("-"),
          datestr = dateparts.reverse().join('/');
      $(this).parent().html(datestr);
    }
    else {
      $(this).parent().html($(this).val());
    }
  });
}

function addClick(btn){
  var pid = $(btn).data('pid'),
    tbody = pid + "-tablebody",
    due_date = "<td><input class='text-center new-mile-field-" + pid + "' type='date'/></td>",
    td = "<td><input class='text-center new-mile-field-" + pid + "' type='number'/></td>",
    tr = "<tr>" + due_date + td + td + td + "</tr>";
  $(tr).appendTo("#" + tbody);

  $(btn).toggleClass('submit');
  $(btn).children('.icons').toggleClass('icons-active');
}

function submitClick(btn) {
  var pid = $(btn).data('pid');
  if(checkRows(pid)) {
    submitRow(pid);
    inputsToCells(pid);

    $(btn).toggleClass('submit');
    $(btn).children('.icons').toggleClass('icons-active');
  }
  else {
    // DO SMARTER ERROR MESSAGE
    alert("Please fill in all the fields!");
  }
}

$(function(){
  $(".add-row-btn").click(function(e){
    if (!$(e.target).hasClass('submit')) {
      addClick(e.target);
    }
    else {
      submitClick(e.target);
    }
  });
});
