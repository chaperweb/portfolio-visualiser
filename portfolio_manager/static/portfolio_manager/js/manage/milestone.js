$.fn.refresh = function() {
    return $(this.selector);
};

function addClick(btn){
  tbody = $(btn).data('pid') + "-tablebody";
  due_date = "<td><input class='text-center' type='date'/></td>";
  td = "<td><input class='text-center' type='number'/></td>";
  tr = "<tr><form>" + due_date + td + td + td + "</form></tr>";
  $(tr).appendTo("#" + tbody);

  $(btn).toggleClass('submit');
  $('.icons').toggleClass('icons-active');
}

function submitClick(btn) {
  alert("THIS SHOULD SUBMIT");

  $(btn).toggleClass('submit');
  $('.icons').toggleClass('icons-active');
}

$(function(){
  $(".add-row-btn").click(function(){
    if (!$(this).hasClass('submit')) {
      addClick(this);
    }
    else {
      submitClick(this);
    }
  });
});
