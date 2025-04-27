$(document).ready(function(){
  $("#changePasswordForm").submit(function(e){
    e.preventDefault();
    $.ajax({
      type: "POST",
      url: "/user/change_password",
      data: $(this).serialize(),
      success: function(resp){
        if(resp.success){
          $("#changePasswordResult").html('<div class="alert alert-success"><i class="bi bi-check-circle"></i> ' + resp.message + '</div>');
          setTimeout(function(){ window.location.href = "/user/profile"; }, 2000);
        } else {
          $("#changePasswordResult").html('<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> ' + resp.message + '</div>');
        }
      },
      error: function(){
        $("#changePasswordResult").html('<div class="alert alert-danger">Beklenmeyen bir hata oluştu.</div>');
      }
    });
  });
});
