'use strict';

const ap_button = $("#claim-ap");

window.onload = function() {
  UpdateApButton(ap_button.data("ap-data"));
}

function UpdateApButton(data) {
  if (data.apAvailable) {
    ap_button.text("AP Please");
    ap_button.addClass("is-primary");
    ap_button.prop('disabled', false);
  } else {
    ap_button.text("AP is Currently Unavailable 😢");
    ap_button.removeClass("is-primary");
    ap_button.prop('disabled', true);
  }
}

function UpdatePage(data) {
  $('#subtotal').text(dollars(data.newTotalInCents));
  UpdateApButton(data);
}

//product-card clicks can togggle checkbox
$('.product-card').on('click', function(e) {
  //if this is not a checkbox card, move on
  var checkBox = $(this).find('.product-checkbox');
  if (checkBox.length === 0) {
    return;
  }

  //if checkbox clicked: ignore and let change handler handle it 
  // prevents error that when checked the card is immeidately auto-unchecked
  if (e.target === checkBox[0]) {
    return;
  }
  
  //Making no action for checkbox when user clicks "Details" carrot icon
  if (e.target.tagName.toLowerCase() === 'details') {
    return;
  }
  
  //if you click on the card outside the checkbox, 
  //toggle the checkbox and trigger change event
  checkBox.click();
});

//When a checkbox toggles off or on, run this code
$(".product-checkbox").change(function() {
  var thisCheckBox = this;
  var parent = $(thisCheckBox).parent();
  $('.product-card').addClass('call-in-progress');
  var productId = parent[0].dataset.product;
  var checkBoxes = $(`.product-card[data-product="${productId}"]`).find('input');
  var parents = checkBoxes.parents();
  checkBoxes.not(thisCheckBox).prop('checked', thisCheckBox.checked);
  parents.addClass('loading');

  let data = $('form').serializeArray();
  data.push({name: 'product', value: productId},
            {name: 'quantity', value: 1});
  if (this.checked) {
    $.ajax({
      url: add_item_url,
      method: 'POST',
      data: data,
      success: function (data) {
        console.log(data);
        if (data.error) {
          location.reload();
        } else if (data.success) {
          resetCountDown();
          var slots = parent[0].dataset.slots.split(',');
          slots.forEach(slot => {
            var conflicts = $(`.slot-${slot}`).not(parents);
            conflicts.addClass(`conflict-${slot}`);
          });
          parents.addClass('claimed');
          UpdatePage(data);
        } else {
          resetCountDown();
          checkBoxes.prop('checked', false);
          parents.addClass('unavailable')
        }

        $('.product-card').removeClass('call-in-progress');
        parents.removeClass('loading');
      },
      error: function (xhr, status, error) {
        location.reload();
      }
    });
  } else {
    $.ajax({
      url: remove_item_url,
      method: 'POST',
      data: data,
      success: function (data) {
        if (data.error) {
          location.reload();
        } else {
          resetCountDown();
          var slots = parent[0].dataset.slots.split(',');
          slots.forEach(slot => {
            var conflicts = $(`.conflict-${slot}`);
            conflicts.removeClass(`conflict-${slot}`);
          });

          $('.product-card').removeClass('call-in-progress');
          parents.removeClass('loading claimed');
          UpdatePage(data);
        }
      },
      error: function (xhr, status, error) {
        console.log('Error - ' + xhr.status + ': ' + xhr.statusText);
        location.reload();
      }
    });
  }
});

// CURRENTLY NOT SUPPORTED: Multi-quantity products with multiple parts across slots

$(".quantity-input").change(function() {
  var thisSelector = this;
  $('.product-card').addClass('call-in-progress');
  var parent = $(thisSelector).parent().parent();
  parent.addClass('loading');
  var productId = parent[0].dataset.product;
  var oldQuantity = parseInt(thisSelector.dataset.quantity);
  var newQuantity = parseInt(thisSelector.value);
  var increment = newQuantity - oldQuantity;
  thisSelector.dataset.quantity = thisSelector.value;
  let data = $('form').serializeArray();
  data.push({name: 'product', value: productId},
            {name: 'quantity', value: Math.abs(increment)});
  if (increment > 0) {
    $.ajax({
      url: add_item_url,
      method: "POST",
      data: data,
      success: function (data) {
        console.log(data);
        if (data.error) {
          location.reload();

        } else if (data.success) {
          resetCountDown();
          var slots = parent[0].dataset.slots.split(',');
          slots.forEach(slot => {
            var conflicts = $(`.slot-${slot}`).not(parent);
            conflicts.addClass(`conflict-${slot}`);
          });
          parent.addClass('claimed');
          UpdatePage(data);
        } else {
          location.reload();
        }

        $('.product-card').removeClass('call-in-progress');
        parent.removeClass('loading');
      },
      error: function (xhr, status, error) {
        location.reload();
      }
    });
  }
  if (increment < 0) {
    $.ajax({
      url: remove_item_url,
      method: "POST",
      data: data,
      success: function (data) {
        if (data.error) {
          location.reload();
        } else {
          resetCountDown();
          var slots = parent[0].dataset.slots.split(',');
          slots.forEach(slot => {
            var conflicts = $(`.conflict-${slot}`);
            conflicts.removeClass(`conflict-${slot}`);
          });
          if (newQuantity == '0') {
            parent.removeClass('claimed');
          }

          $('.product-card').removeClass('call-in-progress');
          parent.removeClass('loading');
          UpdatePage(data);
        }
      },
      error: function (xhr, status, error) {
        location.reload();
      }
    });
  }
});
