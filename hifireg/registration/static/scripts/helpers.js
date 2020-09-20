
// converts total amount to dollars at top of page | No commas per senior dev request
function dollars(value) {
  value = value * 0.01;
  value = value.toFixed(2);
  return "$" + value;
};

