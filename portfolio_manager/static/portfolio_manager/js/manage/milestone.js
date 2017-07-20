$(function(){
  $(".btn").click(function(){
    tbody = $(this).data('pid') + "-tablebody";
    td = "<td></td>";
    tr = "<tr>" + td + td + td + td + "</td>";
    $(tr).appendTo("#" + tbody);
  });
});
