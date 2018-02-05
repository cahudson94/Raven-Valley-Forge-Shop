var addressSelect = document.querySelector('#address_name');
var address1Input = document.getElementById('add_1');
var address2Input = document.getElementById('add_2');
var cityInput = document.getElementById('city');
var stateInput = document.getElementById('state');
var zipcodeInput = document.getElementById('zip');


function populateInfo(Address) {
  // delete the current set of <option> elements out of the
  // day <select>, ready for the next set to be injected
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
    populateInfo(addressSelect.value);
  };
}