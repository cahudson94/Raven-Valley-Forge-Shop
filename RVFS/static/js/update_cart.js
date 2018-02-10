function updatecart(quantity, cart_data) {
  $.get('/shop/cart/update_cart', {quantity, cart_data},
    function(data) {
      var money = 'Total: $' + data;
      $('#total').html(money);
    }
  );
}

$('.delete').click(function () {
  var item;
  var element;
  $('#cart-count').attr('data-count', $('#cart-count').attr('data-count') - 1);
  element = $(this).parent().parent().parent().parent();
  item = $(this).attr('data-item');
  console.log(item);
  $.get('/shop/cart/delete_item', {item},
    function(data) {
      console.log(data);
      if (data !== 'empty') {
        var money = 'Total: $' + data;
        $('#total').html(money);
        while (element.firstChild) {
          element.removeChild(element.firstChild);
        }
        $(element).remove();
      }
      else {
        $('#total').html('Total: $0');
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
        var cart;
        cart = $('#cart');
        var h5 = document.createElement('h5');
        h5.textContent = 'Your cart is empty.';
        h5.className = 'w-100 text-standard';
        var div = document.createElement('div');
        div.className = 'placeholder';
        cart.append(h5);
        cart.append(div);
      }
    }
  );
});
