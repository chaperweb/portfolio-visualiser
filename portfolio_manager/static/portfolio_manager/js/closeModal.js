//closeModal.js is used in fourfield and path templates to hide the modal when
//the snapshot form is filled and sent
window.onload = function() {
  $('#save-path-snap-form').on('submit', function() {
    $('.modal').modal('hide');
  });
  $('#save-fourfield-snap-form').on('submit', function() {
    $('.modal').modal('hide');
  });
};
