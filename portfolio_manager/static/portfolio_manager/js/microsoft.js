$(function(){
  $('.itembtn').click(function(e){
    var win = window.open($(this).data('excelurl'), '_blank');
    if (win) {
      //Browser has allowed it to be opened
      win.focus();
    } else {
      //Browser has blocked it
      alert('Please allow popups for this website');
    }
  });

  $('.import-link, .export-link').click(function(e) {
    $('#loading').show();
  });
});
