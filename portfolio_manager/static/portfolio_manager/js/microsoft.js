$(function(){
  $("#backbtn").click(function(){
    var url = $(this).data('url'),
        parents = JSON.parse($(this).data('parents').replace(/'/g, '"')),
        newItem = parents.shift();

    if(parents.length > 0) {
      var fullUrl = url + '?item_id='+newItem+'&parents=' + JSON.stringify(parents);
    }
    else {
      var fullUrl = url + '?item_id='+newItem
    }
    window.location.assign(fullUrl);
  });
  $(".itembtn").click(function(){
    var url = $(this).data('url'),
        parents = $(this).data('parents'),
        itemid = $(this).data('itemid'),
        current = $(this).data('current');
    if(parents.length > 0) {
      parents = JSON.parse(parents.replace(/'/g, '"'));
    }
    parents.unshift(current);
    var fullUrl = url + '?item_id='+itemid+'&parents=' + JSON.stringify(parents);
    window.location.assign(fullUrl);
  });
});
