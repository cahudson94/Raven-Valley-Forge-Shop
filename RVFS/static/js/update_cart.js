function updatecart(quantity, item_id, type) {
  $.get('/shop/cart/update_cart', {quantity, item_id, type},
    function(data) {
      if (type === 'cart') {
      var money = 'Subtotal: $' + data;
      $('#total').html(money);
    } else {
      var money = 'Pre-order Subtotal: $' + data;
      $('#pre-total').html(money);
    }
    }
  );
}

$('.delete').click(function () {
  var item;
  var element;
  $('#cart-count').attr('data-count', $('#cart-count').attr('data-count') - 1);
  element = $(this).parent().parent().parent().parent();
  type = element.parent().parent()[0].previousSibling.previousSibling.innerHTML
  item = $(this).attr('data-item');
  var target;
  var sectionText;
  if (type === "Pre-orders") {
    type = 'pre';
    target = '#pre-total';
    sectionText = 'Pre-order Subtotal: $'
  } else {
    type = 'cart';
    target = '#total';
    sectionText = 'Subtotal: $'
  }
  $.get('/shop/cart/delete_item', {item, type},
    function(data) {
      if (data !== 'empty') {
        $(target).html(sectionText + data);
        while (element.firstChild) {
          element.removeChild(element.firstChild);
        }
        $(element).remove();
      }
      else {
        $(target).html(sectionText + '0');
        $('.section-head').remove();
        while (element.firstChild) {
          element.removeChild(element.firstChild);
        }
        $(element.parent()).remove();
        $(element).remove();
        var shipping;
        shipping = $('#shipping');
        while (shipping.firstChild) {
          shipping.removeChild(shipping.firstChild);
        }
        $(shipping).remove();
        var h5 = document.createElement('h5');
        if (type === "pre") {
          h5.textContent = 'You are not pre-ordering any items.';
          h5.className = 'w-100 text-standard';
          $('#pre-order').append(h5);
        } else {
          h5.textContent = 'Your cart is empty.';
          h5.className = 'w-100 text-standard';
          $('#cart').append(h5);
        }
      }
    }
  );
});
