
$(".quantity-input").change(function() {
  var thisSelector = this;
  $('input').addClass('call-in-progress');
  var parent = $(thisSelector).parent();
  parent.addClass('loading');
  var productId = parent[0].dataset.product;
  var oldQuantity = parseInt(thisSelector.dataset.quantity);
  var newQuantity = parseInt(thisSelector.value);
  var increment = newQuantity - oldQuantity;
  thisSelector.dataset.quantity = thisSelector.value;
  if (increment > 0) {
    $.ajax({
      url: '/registration/ajax/add_item/',
      data: {
        'product': productId,
        'increment': increment
      },
      dataType: 'json',
      success: function (data) {
        location.reload();
        // console.log(data);
        // if (data.error) {
        //   location.reload();
        //
        // } else if (data.success) {
        //   resetCountDown();
        //
        // } else {
        //   location.reload();
        // }
        //
        // $('.product-card').removeClass('call-in-progress');
        // parent.removeClass('loading');
      },
      error: function (xhr, status, error) {
        location.reload();
      }
    });
  }
  if (increment < 0) {
    $.ajax({
      url: '/registration/ajax/remove_item/',
      data: {
        'product': productId,
        'decrement': increment * -1
      },
      dataType: 'json',
      success: function (data) {

        location.reload();
        // if (data.error) {
        //   location.reload();
        // } else {
        //   resetCountDown();
        //   if (newQuantity == '0') {
        //     parent.removeClass('claimed');
        //   }
        //
        //   $('.product-card').removeClass('call-in-progress');
        //   parent.removeClass('loading');
        // }
      },
      error: function (xhr, status, error) {
        location.reload();
      }
    });
  }
});