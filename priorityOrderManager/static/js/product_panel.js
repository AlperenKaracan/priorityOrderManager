$(document).ready(function(){

  $(".delete-product-btn").click(function(){
    var pid = $(this).data("id");
    $("#deleteProductId").val(pid);
    $("#deleteProductModal").modal("show");
  });

  $("#deleteProductForm").submit(function(e){
    e.preventDefault();
    $.ajax({
      type: "POST",
      url: "/product/delete_product",
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

  $("#addProductForm").submit(function(e){
    e.preventDefault();
    $.ajax({
      type: "POST",
      url: "/product/add_product",
      data: $(this).serialize(),
      success: function(resp){
        if(resp.success){
          $("#addProductResult").html("<div class='alert alert-success'>" + resp.message + "</div>");
          setTimeout(()=>location.reload(), 1000);
        } else {
          $("#addProductResult").html("<div class='alert alert-danger'>Hata: " + resp.message + "</div>");
        }
      },
      error: function(){
        $("#addProductResult").html("<div class='alert alert-danger'>Beklenmeyen bir hata oluştu.</div>");
      }
    });
  });

  $(".update-stock-btn").click(function(){
    var pid = $(this).data("id");
    var name = $(this).data("name");
    var stock = $(this).data("stock");
    $("#updateProductId").val(pid);
    $("#updateProductName").val(name);
    $("#updateNewStock").val(stock);
    $("#updateStockModal").modal("show");
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
          alert("Hata: " + resp.message);
        }
      },
      error: function(){
        alert("Beklenmeyen bir hata oluştu.");
      }
    });
  });
});
