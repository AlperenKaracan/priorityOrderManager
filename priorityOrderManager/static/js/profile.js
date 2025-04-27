$(document).ready(function(){
  $("#updateProfileForm").submit(function(e){
    e.preventDefault();
    $.ajax({
      type: "POST",
      url: "/user/profile",
      data: $(this).serialize(),
      success: function(resp){
        if(resp.success){
          $("#updateProfileResult").html('<div class="alert alert-success"><i class="bi bi-check-circle"></i> ' + resp.message + '</div>');
          setTimeout(()=>location.reload(), 1000);
        } else {
          $("#updateProfileResult").html('<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> Hata: ' + resp.message + '</div>');
        }
      },
      error: function(){
        $("#updateProfileResult").html('<div class="alert alert-danger"><i class="bi bi-exclamation-octagon"></i> Beklenmeyen hata oluştu.</div>');
      }
    });
  });
});
