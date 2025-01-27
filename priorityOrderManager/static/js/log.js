function loadLogs(filter="all"){
    $.get("/api/get_logs", function(res){
        if(!res.success){
            $("#logContainer").html("<div class='text-muted text-center'>Log çekilemedi: "+res.message+"</div>");
            return;
        }
        let data = res.logs;
        if(data.length === 0){
            $("#logContainer").html("<div class='text-muted text-center'>Henüz log yok.</div>");
            return;
        }
        var html = "<ul class='list-unstyled mb-0'>";
        data.forEach(function(log){
            var icon = "<i class='bi bi-info-circle text-secondary me-1'></i>";
            if (log.log_type === "order_created") icon = "<i class='bi bi-plus-circle text-primary me-1'></i>";
            else if (log.log_type === "order_approved") icon = "<i class='bi bi-check-circle text-success me-1'></i>";
            else if (log.log_type === "order_rejected") icon = "<i class='bi bi-x-circle text-danger me-1'></i>";

            const timeStr = (typeof log.timestamp === "string") ? log.timestamp : (new Date(log.timestamp)).toLocaleString();
            html += "<li class='log-item mb-2 slide-in'>" + icon + log.message + " <small class='text-muted'>(" + timeStr + ")</small></li>";
        });
        html += "</ul>";
        $("#logContainer").html(html);
    });
}

$("#logFilter").on("change", function(){
    var selected = $(this).val();
    loadLogs(selected);
});

setInterval(loadLogs, 3000);
loadLogs();
