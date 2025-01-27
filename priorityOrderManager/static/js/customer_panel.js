$(document).ready(function(){
  $(".delete-customer-btn").click(function(){
    var cid = $(this).data("id");
    $("#deleteCustomerId").val(cid);
    $("#deleteCustomerModal").modal("show");
  });

  $("#deleteCustomerForm").submit(function(e){
    e.preventDefault();
    $.ajax({
      type: "POST",
      url: "/customer/delete_customer",
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

  $("#addCustomerForm").submit(function(e){
    e.preventDefault();
    $.ajax({
      type: "POST",
      url: "/customer/add_customer",
      data: $(this).serialize(),
      success: function(resp){
        if(resp.success){
          $("#addCustomerResult").html("<div class='alert alert-success'>" + resp.message + "</div>");
          setTimeout(()=>location.reload(), 1000);
        } else {
          $("#addCustomerResult").html("<div class='alert alert-danger'>Hata: " + resp.message + "</div>");
        }
      },
      error: function(){
        $("#addCustomerResult").html("<div class='alert alert-danger'>Beklenmeyen bir hata oluştu.</div>");
      }
    });
  });
});
