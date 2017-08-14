$(function(){
  $("#backbtn").click(function(){
    var url = $(this).data('url'),
        parents = $(this).data('parents'),
        newItem = parents.shift();
    console.log(typeof parents);

    var url_item_id = 'item_id=' + newItem,
        url_parent = 'parents=' + JSON.stringify(parents),
        url_back = 'back=1';

    if(parents.length > 0) {
      var fullUrl = url + '?'+url_item_id+'&'+url_parent+'&'+url_back;
    }
    else {
      var fullUrl = url + '?'+url_item_id+'&'+url_back;
    }
    window.location.assign(fullUrl);
  });
  $(".itembtn").click(function(){
    var url = $(this).data('url'),
        parents = $(this).data('parents'),
        itemid = $(this).data('itemid'),
        current = $(this).data('current');
    console.log(typeof parents);
    parents.unshift(current);
    var fullUrl = url + '?item_id='+itemid+'&parents=' + JSON.stringify(parents);
    window.location.assign(fullUrl);
  });
});
