(function() {
  var countDownDate;
  resetCountDown = function() {
    countDownDate = new Date().getTime() + 3600000; //1 hour
    document.getElementById("session-expiry-timer").innerHTML = "Your order will expire in: 59:59"
  };
  resetCountDown();
  var countDownInterval;
  if (document.getElementById("session-expiry-timer")) {

    countDownInterval = setInterval(function() {
      // Get today's date and time
      var now = new Date().getTime();

      // Find the distance between now and the count down date
      var distance = countDownDate - now;

      // Time calculations for days, hours, minutes and seconds
      //var days = Math.floor(distance / (1000 * 60 * 60 * 24));
      //var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      var seconds = Math.floor((distance % (1000 * 60)) / 1000);
      if (seconds < 10) {seconds = "0"+seconds;}

      // Display the result in the element with id="demo"
      document.getElementById("session-expiry-timer").innerHTML = "Your order will expire in: " + minutes + ":" + seconds;

      // If the count down is finished, write some text
      if (distance < 0) {
        clearInterval(countDownInterval);
        document.getElementById("session-expiry-timer").innerHTML = "YOUR ORDER HAS EXPIRED";
        setTimeout(function(){ location.reload(); }, 3000);
      }
    }, 1000);
  }
})();