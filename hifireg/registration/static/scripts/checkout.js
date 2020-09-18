function dollars(value) {
  value = value * 0.01;
  value = value.toLocaleString(undefined, {
    'minimumFractionDigits':2, 'maximumFractionDigits':2
  });
  return "$" + value;
};


// when click checkout button
$("#checkoutButton").on("click", function(e){
    e.preventDefault();
    // make request to new_checkout url
    const csrfFormData = $('form').serialize();

    $.post(new_checkout_url, csrfFormData, function(data, status){
        // create instance of Stripe 
        var stripe = Stripe(data.public_key);
        // use Stripe to redirect to Checkout
        stripe.redirectToCheckout({
            sessionId: data.session_id
          }).then(function (result) {
            console.log(result);
            // From Documentation: If `redirectToCheckout` fails due to a browser or network
            // error, display the localized error message to your customer
            // using `result.error.message`.
          });
    });
});


// If payment plan checkbox gets checked
const setDefaultPaymentPlan = (payPerMonthId, monthsId, payPerMonthDefaultValue, monthsDefaultValue) => {
  let checkbox = document.getElementById('checkbox');
  let isChecked = checkbox.checked;
  
  const hiddenForm = document.getElementById('hidden-div');

  if(!isChecked) {
      hiddenForm.classList.add('hidden-div');
      let payPerMonthValue = document.getElementById(payPerMonthId);
      let monthValue = document.getElementById(monthsId);
      payPerMonthValue.value = payPerMonthDefaultValue;
      monthValue.value = monthsDefaultValue;
  }

  if(isChecked) {
      hiddenForm.classList.remove('hidden-div');
  };

  calculateAmountPerPayment();
}

const calculateAmountPerPayment = () => {
  let orderTotal = parseFloat(document.getElementById('order-total').textContent.replace(/[\$,]/g,''));
  let selectedPaymentsPerMonth = document.getElementById('ppm-dropdown');
  let selectedMonths = document.getElementById('months-dropdown');

  for(let i = 0; i < selectedPaymentsPerMonth.children.length; i++) {
      if(selectedPaymentsPerMonth.children[i].selected) {
          var selectedPPMValue = parseInt(selectedPaymentsPerMonth.children[i].value);
      }
  }

  for(let i = 0; i < selectedMonths.children.length; i++) {
      if(selectedMonths.children[i].selected) {
          var selectedMonthsValue = parseInt(selectedMonths.children[i].value);
      }
  }

  let numOfPayments = selectedPPMValue * selectedMonthsValue;
  let amountForEveryPayment = orderTotal / numOfPayments;
  let individualPayment = (Math.floor(100 * amountForEveryPayment)/100).toFixed(2);
  let floorSumofAllPayments = individualPayment * numOfPayments;
  let firstPayment = (Number(individualPayment) + Number(orderTotal - floorSumofAllPayments)).toFixed(2);

  let numOfPaymentsMinusOne = numOfPayments - 1;

  function addDays(date, days) {
      const copy = new Date(Number(date));
      return new Date(copy.setDate(copy.getDate() + days));
  }

  const addMonths = (date, months) => {
      const copy = new Date(Number(date));
      return new Date(copy.setMonth(copy.getMonth() + months));
  }
    
  const date = new Date();
  const dateInTwoWeeks = addDays(date, 14);

  document.getElementById('dueToday').textContent = dollars(100 * firstPayment);

  let arrOfDates = [];

  if(selectedPPMValue === 2) {
      arrOfDates.push(dateInTwoWeeks.toLocaleDateString());
  }

  for(let i = 1; i <= selectedMonthsValue - 1; i++) {
      const newDate = addMonths(date, i);

      arrOfDates.push(newDate.toLocaleDateString());
      
      if(selectedPPMValue === 2) {
          const secondNewDate = addMonths(dateInTwoWeeks, i);
          arrOfDates.push(secondNewDate.toLocaleDateString());
      }
  }

  document.getElementById('payment-options').innerHTML = '';

  for(let i = 0; i < numOfPaymentsMinusOne; i++) {
      document.getElementById('payment-options').innerHTML += `
          <div>
              Due
              <span>${arrOfDates[i]}</span>:
              $<span>${individualPayment}</span>
          </div>
      `;
  }
}
calculateAmountPerPayment();