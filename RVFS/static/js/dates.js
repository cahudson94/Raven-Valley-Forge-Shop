// define variables
var nativePicker = document.querySelector('.nativeDateTimePicker');
var fallbackPicker = document.querySelector('.fallbackDateTimePicker');
var fallbackLabel = document.querySelector('.fallbackLabel');

var yearSelect = document.querySelector('#year');
var monthSelect = document.querySelector('#month');
var daySelect = document.querySelector('#day');
var hourSelect = document.querySelector('#hour');

// hide fallback initially
if (fallbackPicker) {
  fallbackPicker.style.display = 'none';
}
if (fallbackLabel) {
  fallbackLabel.style.display = 'none';
}

// test whether a new datetime-local input falls back to a text input or not
var test = document.createElement('input');
test.type = 'datetime-local';
// if it does, run the code inside the if() {} block
if(test.type === 'text') {
  // hide the native picker and show the fallback
  if (nativePicker) {
    nativePicker.style.display = 'none';
  }
  if (fallbackPicker) {
    fallbackPicker.style.display = 'block';
  }
  if (fallbackLabel) {
    fallbackLabel.style.display = 'block';
  }

  // populate the days and years dynamically
  // (the months are always the same, therefore hardcoded)
  if (monthSelect) {
    populateDays(monthSelect.value);
  }
  populateYears();
  populateHours();
}

function populateDays(month) {
  // delete the current set of <option> elements out of the
  // day <select>, ready for the next set to be injected
  while(daySelect.firstChild){
    daySelect.removeChild(daySelect.firstChild);
  }

  // Create variable to hold new number of days to inject
  var dayNum;

  // 31 or 30 days?
  if(month === 'January' | month === 'March' | month === 'May' | month === 'July' | month === 'August' | month === 'October' | month === 'December') {
    dayNum = 31;
  } else if(month === 'April' | month === 'June' | month === 'September' | month === 'November') {
    dayNum = 30;
  } else {
  // If month is February, calculate whether it is a leap year or not
    var year = yearSelect.value;
    year % 4 === 0 ? dayNum = 29 : dayNum = 28;
  }

  // inject the right number of new <option> elements into the day <select>
  for(var i = 1; i <= dayNum; i++) {
    var option = document.createElement('option');
    option.textContent = i;
    daySelect.appendChild(option);
  }

  // if previous day has already been set, set daySelect's value
  // to that day, to avoid the day jumping back to 1 when you
  // change the year
  if(previousDay) {
    daySelect.value = previousDay;

    // If the previous day was set to a high number, say 31, and then
    // you chose a month with less total days in it (e.g. February),
    // this part of the code ensures that the highest day available
    // is selected, rather than showing a blank daySelect
    if(daySelect.value === '') {
      daySelect.value = previousDay - 1;
    }

    if(daySelect.value === '') {
      daySelect.value = previousDay - 2;
    }

    if(daySelect.value === '') {
      daySelect.value = previousDay - 3;
    }
  }
}

function populateYears() {
  // get this year as a number
  var date = new Date();
  var year = date.getFullYear();

  // Make this year, and the 100 years before it available in the year <select>
  for(var i = 0; i <= 2; i++) {
    var option = document.createElement('option');
    option.textContent = year+i;
    if (yearSelect) {
      yearSelect.appendChild(option);
    }
  }
}

function populateHours() {
  // populate the hours <select> with the 24 hours of the day
  for(var i = 0; i <= 11; i++) {
    var option = document.createElement('option');
    if (i <= 1) {
      option.textContent = '1' + i + ' AM';
    }
    else if (i === 2) {
      option.textContent = '1' + i + ' PM';
    }
    else {
      option.textContent = i - 2 + ' PM';
    }
    if (hourSelect) {
      hourSelect.appendChild(option);
    }
  }
}

// when the month or year <select> values are changed, rerun populateDays()
// in case the change affected the number of available days
if (yearSelect) {
  yearSelect.onchange = function() {
    populateDays(monthSelect.value);
  };
}

if (monthSelect) {
  monthSelect.onchange = function() {
    populateDays(monthSelect.value);
  };
}

//preserve day selection
var previousDay;

// update what day has been set to previously
// see end of populateDays() for usage
if (daySelect) {
  daySelect.onchange = function() {
    previousDay = daySelect.value;
  };
}
