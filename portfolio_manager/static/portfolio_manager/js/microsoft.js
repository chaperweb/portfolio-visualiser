$(function(){
  $('.itembtn').click(function(e){
    var url = $(this).data('url'),
        itemid = $(this).data('itemid');
    window.location.assign(url + '?item_id=' + itemid);
  });
});
