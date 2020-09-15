(function() {
  var volunteerInput = document.querySelector("#id_volunteer_form-wants_to_volunteer");
  function update() {
    if (volunteerInput.value === "False") {
      document.querySelector("#volunteer-details-div").classList.add("hidden-div");
    } else {
      document.querySelector("#volunteer-details-div").classList.remove("hidden-div");
    }
  };
  volunteerInput.onchange = update;
  update();
})();