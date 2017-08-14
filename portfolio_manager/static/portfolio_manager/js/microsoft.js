$(function(){
  $('.itembtn').click(function(e){
    window.location.assign($(this).data('url') + '?item_id=' + $(this).data('itemid'));
  });
});
