function updateOrderTable(){
  $.ajax({
    url: window.location.href,
    success: function(data){
      var newTableBody = $(data).find("#orderTable tbody").html();
      $("#orderTable tbody").fadeOut(300, function(){
        $(this).html(newTableBody).fadeIn(300);
      });
    }
  });
}
setInterval(updateOrderTable, 5000);
