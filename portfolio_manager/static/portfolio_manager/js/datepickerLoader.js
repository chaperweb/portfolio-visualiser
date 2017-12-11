window.onload = function() {
  //test if user is on IE, if so, JQuery datepicker is used on edit-project datefields
  var isIE = /*@cc_on!@*/false || !!document.documentMode;
  if(isIE) {
    $("#date-value").datepicker({dateFormat: "dd/mm/yy"});
  };
};
