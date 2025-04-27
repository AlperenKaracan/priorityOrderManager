function loadPriorityTable(){
  $.get("/order/priority_list", function(data){
    let html = "";
    data.forEach(function(o){
      html += `<tr>
        <td>${o.OrderID}</td>
        <td>${o.CustomerID}</td>
        <td>${o.ProductID}</td>
        <td>${o.Quantity}</td>
        <td>${(o.WaitTime/86400).toFixed(2)}</td>
        <td>${o.DynamicPriority}</td>
      </tr>`;
    });
    $("#priorityTable tbody").html(html);
  });
}
$(document).ready(function(){
  loadPriorityTable();
  setInterval(loadPriorityTable, 5000);
});
