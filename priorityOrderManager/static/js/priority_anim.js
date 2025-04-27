$(document).ready(function(){
  function loadPriorityData(){
    $.get("/order/priority_list", function(data){
      updateTableWithAnimation(data);
    });
  }
  function updateTableWithAnimation(newData){
    let $tbody = $("#priorityTable tbody");
    let newHtml = "";
    newData.forEach(function(o){
      newHtml += `<tr data-orderid="${o.OrderID}">
        <td>${o.OrderID}</td>
        <td>${o.CustomerID}</td>
        <td>${o.ProductID}</td>
        <td>${o.Quantity}</td>
        <td>${(o.WaitTime/86400).toFixed(2)}</td>
        <td>${o.DynamicPriority}</td>
      </tr>`;
    });
    $tbody.fadeOut(300, function(){
      $(this).html(newHtml).fadeIn(300);
    });
  }
  loadPriorityData();
  setInterval(loadPriorityData, 5000);
});
