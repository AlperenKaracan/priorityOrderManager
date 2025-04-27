$(document).ready(function(){
  $(".delete-product-btn").click(function(){
    let pid = $(this).data("id");
    if(confirm("Ürünü silmek istediğinize emin misiniz?")){
      $.post("/product/delete", { product_id: pid }, function(resp){
        if(resp.success){
          alert(resp.message);
          location.reload();
        } else {
          alert("Hata: " + resp.error);
        }
      });
    }
  });
  $("#addProductForm").submit(function(e){
    e.preventDefault();
    $.ajax({
      type: "POST",
      url: "/product/add",
      data: $(this).serialize(),
      success: function(resp){
        if(resp.success){
          $("#addProductResult").html("<div class='alert alert-success'>" + resp.message + " - Yeni ID: " + resp.ProductID + "</div>");
          setTimeout(function(){ location.reload(); }, 1000);
        } else {
          $("#addProductResult").html("<div class='alert alert-danger'>Hata: " + resp.error + "</div>");
        }
      },
      error: function(){
        $("#addProductResult").html("<div class='alert alert-danger'>Beklenmeyen hata oluştu.</div>");
      }
    });
  });

  $("#sliderRange").on("input change", function(){
    let val = $(this).val();
    $("#sliderValue").text(val);
    $("#hiddenAmount").val(val);
  });

  $("#updateStockForm").submit(function(e){
    e.preventDefault();
    $.ajax({
      type: "POST",
      url: "/product/update_stock",
      data: $(this).serialize(),
      success: function(resp){
        if(resp.success){
          alert(resp.message);
          location.reload();
        } else {
          alert("Hata: " + resp.error);
        }
      },
      error: function(){
        alert("Beklenmeyen hata oluştu.");
      }
    });
  });
});
