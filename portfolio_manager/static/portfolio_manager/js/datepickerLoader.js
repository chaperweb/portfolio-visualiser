window.onload = function() {
  //test if user is on firefox or IE, if so, JQuery datepicker is used on edit-project datefields
  var isFirefox = typeof InstallTrigger !== 'undefined';
  var isIE = /*@cc_on!@*/false || !!document.documentMode;
  if(isFirefox || isIE) {
    $("#date-value").datepicker({dateFormat: "dd/mm/yy"});
  };
};
