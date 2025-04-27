function loadLogs(){
  let selectedFilters = [];
  $("input[name='log_type']:checked").each(function(){
    selectedFilters.push($(this).val());
  });
  let filterParam = selectedFilters.join(',');
  $.get("/logs/list", { log_type: filterParam }, function(data){
    if(data.error){
      $("#logContainer").html("<div class='alert alert-danger'>Hata: " + data.error + "</div>");
      return;
    }
    if(data.length === 0){
      $("#logContainer").html("<div class='text-muted text-center'>Henüz log yok.</div>");
      return;
    }
    let html = "<ul class='list-unstyled'>";
    data.forEach(function(log){
      let icon = "<i class='bi bi-info-circle text-secondary me-1'></i>";
      if(log.log_type.includes("order_created"))
        icon = "<i class='bi bi-plus-circle text-primary me-1'></i>";
      else if(log.log_type.includes("order_approved"))
        icon = "<i class='bi bi-check-circle text-success me-1'></i>";
      else if(log.log_type.includes("order_rejected"))
        icon = "<i class='bi bi-x-circle text-danger me-1'></i>";
      html += `<li class="log-item">${icon} ${log.message} <small class="text-muted">(${log.timestamp})</small></li>`;
    });
    html += "</ul>";
    $("#logContainer").html(html);
  });
}

$(document).ready(function(){
  $("input[name='log_type']").on("change", loadLogs);
  setInterval(loadLogs, 3000);
  loadLogs();
});
