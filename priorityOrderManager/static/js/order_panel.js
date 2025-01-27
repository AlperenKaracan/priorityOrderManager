$(document).ready(function(){
  $("#test-system-btn").click(function(){
    if(confirm("Sistemi test etmek istediğinize emin misiniz?")){
      $.post("/order/test_system", {}, function(data){
        if(data.success){
          alert(data.message);
        } else {
          alert("Hata: " + data.message);
        }
      }).fail(function(){
        alert("Beklenmeyen bir hata oluştu.");
      });
    }
  });

  $(".approve-order-btn").click(function(){
    var oid = $(this).data("id");
    $("#actionOrderId").val(oid);
    $("#actionOrderType").text("onaylamak");
    $("#actionOrderModal").modal("show");
  });

  $(".reject-order-btn").click(function(){
    var oid = $(this).data("id");
    $("#actionOrderId").val(oid);
    $("#actionOrderType").text("reddetmek");
    $("#actionOrderModal").modal("show");
  });

  $("#actionOrderForm").submit(function(e){
    e.preventDefault();
    var actionType = $("#actionOrderType").text();
    var url = (actionType === "onaylamak") ? "/order/approve_order" : "/order/reject_order";
    $.ajax({
      type: "POST",
      url: url,
      data: $(this).serialize(),
      success: function(resp){
        if(resp.success){
          alert(resp.message);
          location.reload();
        } else {
          alert("Hata: " + resp.message);
        }
      },
      error: function(){
        alert("Beklenmeyen bir hata oluştu.");
      }
    });
  });
});
