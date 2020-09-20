// this large anon function protects my "global variables on this page"
(function() {
  var selectAllCheckbox = document.querySelector("#selectAll");
  var label = document.querySelector("#selectAllLabel");  
  var invoiceCheckboxes = document.querySelectorAll("#invoiceTable input");
  var payInvoicesButton = document.querySelector("#payInvoicesButton")

  var selectAllText = "Select All Invoices";
  var unselectAllText = "Unselect Invoices"

  // toggle HTML for select all checkbox
  selectAllCheckbox.onchange = function() {
    if (selectAllCheckbox.checked === false) {
      selectAll(false);
      label.innerHTML = selectAllText;
    } else {
      label.innerHTML = unselectAllText;
      selectAll(true);
    }
    updateTotal();
  };

  // logic for select/unselect all checkboxs on invoices.html
  function selectAll(checked) {
    for (var i = 0; i < invoiceCheckboxes.length; i++) {
      if (invoiceCheckboxes[i].type == 'checkbox') {
        invoiceCheckboxes[i].checked = checked;
      }  
    }
  };

  // catch logic for chronological due date pay requirement
  function checkAllPriorInvoices(checkbox) {
    var i = 0;
    while (invoiceCheckboxes[i] !== checkbox) {
      invoiceCheckboxes[i].checked = true;
      i += 1;
    }
  };

  function uncheckAllFutureInvoices(checkbox) {
    var i = invoiceCheckboxes.length - 1;
    while (invoiceCheckboxes[i] !== checkbox) {
      invoiceCheckboxes[i].checked = false;
      i -= 1;
    }
  };

  // this dynamic query is called in several functions
  function getCheckedCheckboxes() {
    return document.querySelectorAll("#invoiceTable input:checked");
  }

  function onCheckboxChange(e) {
    if (e.target.checked) {
      checkAllPriorInvoices(e.target);
    } else {
      uncheckAllFutureInvoices(e.target);
    }
    var checkedCheckboxes = getCheckedCheckboxes();
    if (checkedCheckboxes.length === invoiceCheckboxes.length) {
      label.innerHTML = unselectAllText;
      selectAllCheckbox.checked = true;
    } else {
      label.innerHTML = selectAllText;
      selectAllCheckbox.checked = false;
    }
    updateTotal();
  };

  // sums up pay amount based on checked boxes
  invoiceCheckboxes.forEach(function(checkbox){
    checkbox.onchange = onCheckboxChange;
  });
  
  function updateTotal() {
    var amountDue = calculateTotalPaymentAmount();
    document.querySelector("#amountDue").innerHTML = dollars(amountDue);
    payInvoicesButton.disabled = amountDue === 0;
  };

  function calculateTotalPaymentAmount() {
    var checkedCheckboxes = getCheckedCheckboxes();
    var amount = 0;

    checkedCheckboxes.forEach(function(checkbox){
        amount += parseInt(checkbox.dataset.amount);
    });
    return amount;
  };


  
  // AJAX (for brevity sake) request to Stripe API
  payInvoicesButton.onclick = function(e){
    e.preventDefault();
    var amount = calculateTotalPaymentAmount();

    $.get(pay_invoices_url + "?amount=" + amount, function(data, status){
        var stripe = Stripe(data.public_key);
       
        stripe.redirectToCheckout({
          sessionId: data.session_id
        }).then(function (result) {
          console.log(result);
        });
    });
  };

  updateTotal();
})();


