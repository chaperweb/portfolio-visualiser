$(function(){
  $(".btn").click(function(){
    tbody = $(this).data('pid') + "-tablebody";
    due_date = "<td><input class='text-center' type='date'/></td>"
    td = "<td><input class='text-center' type='number'/></td>";
    tr = "<tr><form>" + due_date + td + td + td + "</form></tr>";
    $(tr).appendTo("#" + tbody);
  });
});
