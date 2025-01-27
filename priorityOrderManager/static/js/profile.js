$(document).ready(function(){
  $("#updateProfileForm").submit(function(e){
    e.preventDefault();
    $.ajax({
      type: "POST",
      url: "/user/profile",
      data: $(this).serialize(),
      success: function(resp){
        if(resp.success){
          $("#updateProfileResult").html("<div class='alert alert-success'>" + resp.message + "</div>");
          setTimeout(()=>location.reload(), 1000);
        } else {
          $("#updateProfileResult").html("<div class='alert alert-danger'>Hata: " + resp.message + "</div>");
        }
      },
      error: function(){
        $("#updateProfileResult").html("<div class='alert alert-danger'>Beklenmeyen bir hata oluştu.</div>");
      }
    });
  });
});
