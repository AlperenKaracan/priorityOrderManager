$(document).ready(function(){
  $(".deleteBtn").click(function(){
    let cid = $(this).data("customer-id");
    if(confirm("Müşteriyi silmek istediğinize emin misiniz?")){
      $.post("/customers/delete", { customer_id: cid }, function(resp){
        if(resp.success){
          alert(resp.message);
          location.reload();
        } else {
          alert("Hata: " + resp.error);
        }
      });
    }
  });

  $("#addCustomerForm").submit(function(e){
    e.preventDefault();
    $.post("/customers/add", $(this).serialize(), function(resp){
      if(resp.success){
        $("#addCustomerResult").html("<div class='alert alert-success'>" + resp.message + "</div>");
        setTimeout(()=>location.reload(), 1000);
      } else {
        $("#addCustomerResult").html("<div class='alert alert-danger'>Hata: " + resp.error + "</div>");
      }
    });
  });

  $(".updateBudgetBtn").click(function(){
    let cid = $(this).data("customer-id");
    let currentBudget = $(this).data("current-budget");
    $("#updateCustomerId").val(cid);
    $("#currentBudget").val(currentBudget);
    $("#newBudget").val("");
    $("#updateBudgetResultModal").html("");
    let modal = new bootstrap.Modal(document.getElementById("updateBudgetModal"));
    modal.show();
  });

  $("#updateBudgetForm").submit(function(e){
    e.preventDefault();
    $.ajax({
      type: "POST",
      url: "/customers/update_budget",
      data: $(this).serialize(),
      success: function(resp){
        if(resp.success){
          $("#updateBudgetResultModal").html('<div class="alert alert-success">Bütçe güncellendi.</div>');
          setTimeout(()=>location.reload(), 1000);
        } else {
          $("#updateBudgetResultModal").html('<div class="alert alert-danger">Hata: ' + resp.error + '</div>');
        }
      },
      error: function(){
        $("#updateBudgetResultModal").html('<div class="alert alert-danger">Beklenmeyen hata oluştu.</div>');
      }
    });
  });
});
