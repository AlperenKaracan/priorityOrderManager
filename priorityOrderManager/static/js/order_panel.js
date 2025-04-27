$(document).ready(function(){
  $("#orderForm").submit(function(e){
    e.preventDefault();
    $("#orderResult").html('<div class="alert alert-info"><i class="bi bi-hourglass-split"></i> Sipariş gönderiliyor...</div>');
    $.ajax({
      type: "POST",
      url: "/order/create",
      data: $(this).serialize(),
      success: function(response){
        if(response.success){
          $("#orderResult").html('<div class="alert alert-success"><i class="bi bi-check-circle"></i> Sipariş oluşturuldu. Sipariş ID: ' + response.order_id + '</div>');
          $("#orderForm")[0].reset();
          confettiEffect();
          updateOrderTable();
          updateProductList();
        } else {
          $("#orderResult").html('<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> Hata: ' + response.message + '</div>');
        }
      },
      error: function(){
        $("#orderResult").html('<div class="alert alert-danger"><i class="bi bi-exclamation-octagon"></i> Beklenmeyen hata oluştu.</div>');
      }
    });
  });

  $("#test-system-btn").click(function(){
    if(confirm("Sistemi test etmek istediğinize emin misiniz?")){
      var $btn = $(this);
      $btn.prop("disabled", true).html('<i class="bi bi-gear"></i> Test Ediliyor...');
      $.ajax({
        type: "POST",
        url: "/order/test_bulk_orders",
        success: function(response){
          if(response.success){
            $("#testResult").html('<div class="alert alert-success"><i class="bi bi-check-circle"></i> ' + response.message + '</div>');
            confettiEffect();
            updateOrderTable();
            updateProductList();
          } else {
            $("#testResult").html('<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> Hata: ' + response.message + '</div>');
          }
        },
        error: function(){
          $("#testResult").html('<div class="alert alert-danger"><i class="bi bi-exclamation-octagon"></i> Beklenmeyen hata oluştu.</div>');
        },
        complete: function(){
          $btn.prop("disabled", false).html('<i class="bi bi-gear"></i> Sistemi Test Et');
        }
      });
    }
  });
});

function confettiEffect(){
  let confettiContainer = $('<div id="confettiContainer"></div>').css({
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
    zIndex: 9999
  });
  $('body').append(confettiContainer);
  for(let i = 0; i < 100; i++){
    let confetti = $('<div class="confetti"></div>').css({
      position: 'absolute',
      top: Math.random()*100 + '%',
      left: Math.random()*100 + '%',
      width: '8px',
      height: '8px',
      backgroundColor: 'hsl(' + (Math.random()*360) + ', 100%, 50%)',
      opacity: 0.8,
      transform: 'rotate(' + Math.random()*360 + 'deg)'
    });
    confettiContainer.append(confetti);
    confetti.animate({ top: '110%' }, Math.random()*2000+1500, "linear", function(){
      $(this).remove();
    });
  }
  setTimeout(function(){
    confettiContainer.remove();
  }, 3000);
}

let lastTableContent = "";
function updateOrderTable(){
  $.ajax({
    url: window.location.href,
    success: function(data){
      let newTableBody = $(data).find("#orderTable tbody").html();
      if(newTableBody !== lastTableContent){
         lastTableContent = newTableBody;
         $("#orderTable tbody").fadeOut(300, function(){
           $(this).html(newTableBody).fadeIn(300);
         });
      }
    }
  });
}
setInterval(updateOrderTable, 5000);

function updateProductList(){
  $.get("/product/list_json", function(data){
    if(data.success){
      let select = $("select[name='product_id']");
      select.empty();
      data.products.forEach(function(p){
        select.append(`<option value="${p.ProductID}">${p.ProductName} - Fiyat: ${p.Price} TL, Kalan Stok: ${p.Stock}</option>`);
      });
    }
  });
}
