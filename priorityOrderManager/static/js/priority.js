function loadPriorityTable(){
  $.get("/order/priority_list", function(data){
    var html = "";
    data.forEach(function(o){
      html += `
        <tr class="priority-row">
          <td>${o.OrderID}</td>
          <td>${o.CustomerName}</td>
          <td>${o.ProductName}</td>
          <td>${o.Quantity}</td>
          <td>${o.WaitDays}</td>
          <td>${o.DynamicPriority}</td>
        </tr>
      `;
    });
    $("#priorityTable tbody").html(html);
  });
}

$(document).ready(function(){
  loadPriorityTable();
  setInterval(loadPriorityTable, 3000);
});
