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

  if (this.checked) {
    $.ajax({
      url: '/registration/ajax/add_item/',
      data: {
        'product': productId,
        'increment': 1
      },
      dataType: 'json',
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
      url: '/registration/ajax/remove_item/',
      data: {
        'product': productId,
        'decrement': 1
      },
      dataType: 'json',
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

$(".product-increment").click(function() {
  var thisButton = this;
  var parent = $(thisButton).parent().parent();
  var productId = parent[0].dataset.product;
  $('.product-card').addClass('call-in-progress');
  parent.addClass('loading');

  $.ajax({
    url: '/registration/ajax/add_item/',
    data: {
      'product': productId,
      'increment': 1
    },
    dataType: 'json',
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
        var quantity = parent.find('.quantity-claimed');
        quantity.text(parseInt(quantity.text()) + 1);
        parent.removeClass('minimum maximum');
        parent.addClass('claimed');
        if (quantity.text() == parent[0].dataset.max) {
          parent.addClass('maximum')
        }

      } else {
        parent.addClass('unavailable')
      }

      $('.product-card').removeClass('call-in-progress');
      parent.removeClass('loading');
    },
    error: function (xhr, status, error) {
      location.reload();
    }
  });
});

$(".product-decrement").click(function() {
  var thisButton = this;
  var parent = $(thisButton).parent().parent();
  var productId = parent[0].dataset.product;
  $('.product-card').addClass('call-in-progress');
  parent.addClass('loading');

  $.ajax({
    url: '/registration/ajax/remove_item/',
    data: {
      'product': productId,
      'decrement': 1
    },
    dataType: 'json',
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
        var quantity = parent.find('.quantity-claimed');
        quantity.text(parseInt(quantity.text()) - 1);
        parent.removeClass('minimum maximum');
        if (quantity.text() == '0') {
          parent.addClass('minimum').removeClass('claimed');
        }

        $('.product-card').removeClass('call-in-progress');
        parent.removeClass('loading');
      }
    },
    error: function (xhr, status, error) {
      location.reload();
    }
  });
});