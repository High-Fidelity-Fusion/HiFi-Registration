// when click checkout button
$("#checkoutButton").on("click", function(e){
    e.preventDefault();
    // make request to new_checkout url
    $.get("/registration/payment/new_checkout", function(data, status){
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


