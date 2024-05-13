let autocomplete;

function initAutoComplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById("id_address"),
    {
      types: ["geocode", "establishment"],
      componentRestrictions: { country: ["in"] },
    }
  );
  autocomplete.addListener("place_changed", OnPlaceChanged);
}

function OnPlaceChanged() {
  let place = autocomplete.getPlace();
  if (!place.geometry) {
    address.placeholder = "Start Typing";
  } else {
    // console.log(place);
  }

  let geocoder = new google.maps.Geocoder();
  let address = document.getElementById("id_address").value;

  geocoder.geocode({ address: address }, function (results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      let latitude = results[0].geometry.location.lat();
      let longitude = results[0].geometry.location.lng();

      document.getElementById("id_address").value = address;
      document.getElementById("id_latitude").value = latitude;
      document.getElementById("id_longitude").value = longitude;
    }
  });


  for (let i = 0; i < place.address_components.length; i++) {
    for (let j = 0; j < place.address_components[i].types.length; j++) {
      if (place.address_components[i].types[j] == "country") {
        document.getElementById("id_country").value =
          place.address_components[i].long_name;
      }

      if (
        place.address_components[i].types[j] == "administrative_area_level_1"
      ) {
        document.getElementById("id_state").value =
          place.address_components[i].long_name;
      }

      if (place.address_components[i].types[j] == "locality") {
        document.getElementById("id_city").value =
          place.address_components[i].long_name;
      }

      if (place.address_components[i].types[j] == "postal_code") {
        document.getElementById("id_pin_code").value =
          place.address_components[i].long_name;
      } else {
        document.getElementById("id_pin_code").value = "";
      }
    }
  }
}


// ADD TO CART FUNCTIONALITY
const addToCartButtons = document.querySelectorAll('.add_to_cart');
addToCartButtons.forEach(addToCartButton => {
  addToCartButton.addEventListener('click', (event) => {
    event.preventDefault();
  
    // Extracting data URL
    const url = addToCartButton.getAttribute('data-url');
    const food_id = addToCartButton.getAttribute('data-id');
    
    // Sending request to Django backend
    fetch(url, {
      method: 'GET', 
      headers: {
        'Content-Type': 'application/json',
      },
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      // Handle response data as needed
      // alert(data.message);
      if (data.status == 'login_required') {
        swal(data.message, '', 'info').then(()=>{
          window.location = '/login';
        })
      } else if (data.status == 'Failed') {
        swal(data.message, '', 'error');
      } else {
        document.getElementById('cart_counter').innerHTML = data.cart_counter['cart_count']
        document.getElementById('cart_quantity-' + food_id).innerHTML = data.qty;
      } 
    })
    .catch(error => {
      console.error('There was a problem with the fetch operation:', error);
    });
  });
});

// Place the cart item quantity on load
const item_qty_all = document.querySelectorAll('.item_qty');
item_qty_all.forEach(item_qty=>{
  let id =  item_qty.getAttribute('id');
  let quantity =  item_qty.getAttribute('data-qty');
  document.getElementById(id).textContent = quantity;
})


// REMOVE FROM CART FUNCTIONALITY
const removeFromCartButtons = document.querySelectorAll('.remove_from_cart');
removeFromCartButtons.forEach(removeFromCartButton => {
  removeFromCartButton.addEventListener('click', (event) => {
    event.preventDefault();
  
    // Extracting data URL
    const url = removeFromCartButton.getAttribute('data-url');
    const food_id = removeFromCartButton.getAttribute('data-id');
    
    // Sending request to Django backend
    fetch(url, {
      method: 'GET', 
      headers: {
        'Content-Type': 'application/json',
      },
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      // Handle response data as needed
      // alert(data.message);
      if (data.status == 'login_required') {
        swal(data.message, '', 'info').then(()=>{
          window.location = '/login';
        })
      } else if (data.status == 'Failed') {
        swal(data.message, '', 'error');
      } else {
        document.getElementById('cart_counter').innerHTML = data.cart_counter['cart_count']
        document.getElementById('cart_quantity-' + food_id).innerHTML = data.qty;
      } 
    })
    .catch(error => {
      console.error('There was a problem with the fetch operation:', error);
    });
  });
});

// Place the cart item quantity on load
// const item_qty_all = document.querySelectorAll('.item_qty');
// item_qty_all.forEach(item_qty=>{
//   let id =  item_qty.getAttribute('id');
//   let quantity =  item_qty.getAttribute('data-qty');
//   document.getElementById(id).textContent = quantity;
// })