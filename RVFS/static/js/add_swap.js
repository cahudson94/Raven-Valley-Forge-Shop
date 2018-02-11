var addressSelect = document.querySelector('#ship_address_name');
var servaddressSelect = document.querySelector('#serv_address_name');

function populateInfo(Address, type) {
  // delete the current set of <option> elements out of the
  // day <select>, ready for the next set to be injected
  if (type === 'ship') {
    var address1Input = document.getElementById('ship_add_1');
    var address2Input = document.getElementById('ship_add_2');
    var cityInput = document.getElementById('ship_city');
    var stateInput = document.getElementById('ship_state');
    var zipcodeInput = document.getElementById('ship_zip');
  }
  else {
    var address1Input = document.getElementById('serv_add_1');
    var address2Input = document.getElementById('serv_add_2');
    var cityInput = document.getElementById('serv_city');
    var stateInput = document.getElementById('serv_state');
    var zipcodeInput = document.getElementById('serv_zip');
  }
  var add = Address.slice(1, -1).split(', ');
  for (var i = 0; i<add.length; i++) {
    if (add[i].split(': ')[0].slice(1, -1) === 'address1') {
      var address1 = add[i].split(': ')[1].slice(1, -1);
    }
    if (add[i].split(': ')[0].slice(1, -1) === 'address2') {
      var address2 = add[i].split(': ')[1].slice(1, -1);
    }
    if (add[i].split(': ')[0].slice(1, -1) === 'zip_code') {
      var zip_code = add[i].split(': ')[1].slice(1, -1);
    }
    if (add[i].split(': ')[0].slice(1, -1) === 'city') {
      var city = add[i].split(': ')[1].slice(1, -1);
    }
    if (add[i].split(': ')[0].slice(1, -1) === 'state') {
      var state = add[i].split(': ')[1].slice(1, -1);
    }
  }
  address1Input.value = address1;
  address2Input.value = address2;
  cityInput.value = city;
  stateInput.value = state;
  zipcodeInput.value = zip_code;
}




if (addressSelect) {
  addressSelect.onchange = function() {
    populateInfo(addressSelect.value, 'ship');
  };
}

if (servaddressSelect) {
  servaddressSelect.onchange = function() {
    populateInfo(servaddressSelect.value, 'serv');
  };
}
