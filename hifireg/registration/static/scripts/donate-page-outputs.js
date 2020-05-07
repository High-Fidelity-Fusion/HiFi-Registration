function calculateOutputs() {
        var donation = document.getElementById("id_donation").value * 100
        var subtotal = document.getElementById("id_subtotal").innerHTML.substring(1) * 100
        document.getElementById('id_total').innerHTML = "$" + ((subtotal + donation) * .01).toFixed(2)
    }