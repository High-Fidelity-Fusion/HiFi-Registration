"use strict";

const donation_input = document.getElementById("donation_input");
const donation_hidden_input = document.getElementById("id_donation");
const total_output = document.getElementById("id_total");
const currency_pattern = /^\$?([0-9]*\.?[0-9]?[0-9]?)/;
const subtotal = Number(document.getElementById("id_subtotal").innerHTML.substring(1));

window.onload = function() {
    donation_input.addEventListener("input", calculateOutputs);
    donation_input.addEventListener("blur", reformatDisplay);
    donation_input.addEventListener("click", function() {this.select()}) // select all input on click
    calculateOutputs();
}

function calculateOutputs() {
    /**
     * Clean the input by overwriting the value with the part that matches the
     * currency pattern and handle the "." case. Note that a group is captured
     * by the regex, that group is the entire number with the dollar sign.
     */ 
    let donation_string = donation_input.value.match(currency_pattern)[1];
    if(donation_string == ".") {
        donation_string = "0.";
    }
    donation_input.value = "$" + donation_string;
    
    /* update hidden form input and output */
    const donation = Number(donation_string);
    donation_hidden_input.value = donation * 100;
    total_output.textContent = "$" + (subtotal + donation).toFixed(2);
}

function reformatDisplay() {
    /* Reformat the display to show both zeros of the currency */
    donation_input.value = "$" + Number(donation_input.value.substring(1)).toFixed(2);
}
