"use strict";

window.onload = function() {
    let donation_el = document.getElementById("id_donation");
    donation_el.addEventListener("input", calculateOutputs);
    calculateOutputs();
}

function calculateOutputs() {
    let donation = document.getElementById("id_donation").value * 100;
    let subtotal = document.getElementById("id_subtotal").innerHTML.substring(1) * 100;

    document.getElementById('id_total').innerHTML = "$" + ((subtotal + donation) * .01).toFixed(2)
}
