$(document).ready(function(){
  function loadPriorityData(){
    $.get("/order/priority_list", function(data){
      updateTableWithAnimation(data);
    });
  }

  function updateTableWithAnimation(newData){
    let $tbody = $("#priorityTable tbody");
    let oldRows = $tbody.find("tr");
    let oldMap = {};

    oldRows.each(function(idx, tr){
      let orderId = $(tr).data("orderid");
      oldMap[orderId] = $(tr);
    });


    let newHtml = "";
    newData.forEach(function(o){
      newHtml += `
        <tr data-orderid="${o.OrderID}">
          <td>${o.OrderID}</td>
          <td>${o.CustomerName}</td>
          <td>${o.ProductName}</td>
          <td>${o.Quantity}</td>
          <td>${o.WaitDays}</td>
          <td>${o.DynamicPriority}</td>
        </tr>`;
    });


    $tbody.fadeOut(300, function(){
      $tbody.html(newHtml);
      $tbody.fadeIn(300);
    });
  }

  loadPriorityData();
  setInterval(loadPriorityData, 5000);
});
