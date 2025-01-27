function updateOrderTable(){
    $.get(window.location.href, function(data){
        var newBody = $(data).find("#orderTable tbody");
        $("#orderTable tbody").replaceWith(newBody);
    });
}
setInterval(updateOrderTable, 3000);
