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
const addToCartButtons = document.querySelectorAll(".add_to_cart");
addToCartButtons.forEach((addToCartButton) => {
  addToCartButton.addEventListener("click", (event) => {
    event.preventDefault();

    // Extracting data URL
    const url = addToCartButton.getAttribute("data-url");
    const food_id = addToCartButton.getAttribute("data-id");

    // Sending request to Django backend
    fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        // Handle response data as needed
        // alert(data.message);
        if (data.status == "login_required") {
          swal(data.message, "", "info").then(() => {
            window.location = "/login";
          });
        } else if (data.status == "Failed") {
          swal(data.message, "", "error");
        } else {
          document.getElementById("cart_counter").innerHTML =
            data.cart_counter["cart_count"];
          document.getElementById("cart_quantity-" + food_id).innerHTML =
            data.qty;

          // Update subtotal, tax and grand total
          if (window.location.pathname == "/cart/") {
            applyCartAmounts(
              data.cart_amount["subtotal"],
              data.cart_amount["tax_dict"],
              data.cart_amount["grand_total"]
            );
          }
        }
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
      });
  });
});

// Place the cart item quantity on load
const item_qty_all = document.querySelectorAll(".item_qty");
item_qty_all.forEach((item_qty) => {
  let id = item_qty.getAttribute("id");
  let quantity = item_qty.getAttribute("data-qty");
  document.getElementById(id).textContent = quantity;
});

// DECREASE CART ITEM FUNCTIONALITY
const decreaseInCartButtons = document.querySelectorAll(".decrease_in_cart");
decreaseInCartButtons.forEach((decreaseInCartButton) => {
  decreaseInCartButton.addEventListener("click", (event) => {
    event.preventDefault();

    // Extracting data URL
    const url = decreaseInCartButton.getAttribute("data-url");
    const food_id = decreaseInCartButton.getAttribute("data-id");
    const cart_id = decreaseInCartButton.getAttribute("id");

    // Sending request to Django backend
    fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        // Handle response data as needed
        // alert(data.message);
        if (data.status == "login_required") {
          swal(data.message, "", "info").then(() => {
            window.location = "/login";
          });
        } else if (data.status == "Failed") {
          swal(data.message, "", "error");
        } else {
          document.getElementById("cart_counter").innerHTML =
            data.cart_counter["cart_count"];
          document.getElementById("cart_quantity-" + food_id).innerHTML =
            data.qty;

          if (window.location.pathname == "/cart/") {
            removeItemFromCartZero(data.qty, cart_id);
            checkForEmptyCart(data.cart_counter["cart_count"]);
            // Update subtotal, tax and grand total
            applyCartAmounts(
              data.cart_amount["subtotal"],
              data.cart_amount["tax_dict"],
              data.cart_amount["grand_total"]
            );
          }
        }
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
      });
  });
});

// REMOVE ITEM FUNCTIONALITY
const removeFromCartButtons = document.querySelectorAll(
  ".remove_item_from_cart"
);
removeFromCartButtons.forEach((removeFromCartButton) => {
  removeFromCartButton.addEventListener("click", (event) => {
    event.preventDefault();

    // Extracting data URL
    const url = removeFromCartButton.getAttribute("data-url");
    const cart_id = removeFromCartButton.getAttribute("data-id");

    // Sending request to Django backend
    fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        // Handle response data as needed
        // alert(data.message);
        if (data.status == "Failed") {
          swal(data.message, "", "error");
        } else {
          document.getElementById("cart_counter").innerHTML =
            data.cart_counter["cart_count"];
          swal(data.status, data.message, "success");
          removeItemFromCartZero(0, cart_id);
          checkForEmptyCart(data.cart_counter["cart_count"]);

          if (window.location.pathname == "/cart/") {
            // Update subtotal, tax and grand total
            applyCartAmounts(
              data.cart_amount["subtotal"],
              data.cart_amount["tax_dict"],
              data.cart_amount["grand_total"]
            );
          }
        }
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
      });
  });
});

// REMOVE ITEM FROM CART IF QUANTITY IS ZERO
function removeItemFromCartZero(itemQuantity, cart_id) {
  if (itemQuantity <= 0) {
    document.getElementById(`cart-item-${cart_id}`).remove();
  }
}

// CHECK FOR EMPTY CART TO SHOW MESSAGE
function checkForEmptyCart(cart_quantity) {
  if (cart_quantity <= 0) {
    document.getElementById("empty-cart").style.display = "";
  }
}

// APPLY CART AMOUNTS
function applyCartAmounts(subtotal, tax_dict, grandtotal) {
  document.querySelector("#subtotal").innerHTML = subtotal;

  for (key1 in tax_dict) {
    for(key2 in tax_dict[key1]) {
      document.querySelector(`#tax-${key1}`).innerHTML = tax_dict[key1][key2];
    }
  }
  document.querySelector("#total").innerHTML = grandtotal;
}

// ADD BUSINESS HOURS
const addBusinessHoursButton = document.querySelector(
  ".add_business_hours_button"
);

addBusinessHoursButton.addEventListener("click", (event) => {
  event.preventDefault();
  let day = document.getElementById("id_day").value;
  let from_hour = document.getElementById("id_from_hour").value;
  let to_hour = document.getElementById("id_to_hour").value;
  let is_closed = document.getElementById("id_is_closed").checked;
  let csrf_token = document.querySelector(
    'input[name="csrfmiddlewaretoken"]'
  ).value;
  let url = document.querySelector("#add_business_hours_url").value;

  if (is_closed) {
    is_closed = "True";
    condition = "day != ''";
  } else {
    is_closed = "False";
    condition = "day != '' && from_hour != '' && to_hour != ''";
  }

  let data = {
    day: day,
    from_hour: from_hour,
    to_hour: to_hour,
    is_closed: is_closed,
  };

  console.log(data);

  if (eval(condition)) {
    // Sending the data to django backend using fetch API
    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrf_token,
      },
      body: JSON.stringify(data),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok " + response.statusText);
        }
        return response.json();
      })
      .then((data) => {
        if (data.status == "success") {
          const tbody = document.querySelector(".table_business_hours tbody");
          const newRow = document.createElement("tr");
          newRow.setAttribute("id", `day-${data.id}`);
          const newCell1 = document.createElement("td");
          newCell1.textContent = data.day;
          const newCell2 = document.createElement("td");
          if (data.is_closed) {
            newCell2.innerHTML = "<b>Closed</b>";
          } else {
            newCell2.textContent = `${data.from_hour} - ${data.to_hour}`;
          }
          const newCell3 = document.createElement("td");
          newCell3.innerHTML = `
    <button class="btn btn-danger business_hours_remove_button" type="button" onclick="removeBusinessHour(${data.id})">Remove</button>
`;
          newRow.appendChild(newCell1);
          newRow.appendChild(newCell2);
          newRow.appendChild(newCell3);
          tbody.appendChild(newRow);
          document.getElementById("business_hours").reset();
        } else {
          swal(data.message, "", "error");
        }
      })
      .catch((error) => {
        swal(error, "", danger);
      });
  } else {
    swal("Please fill all the fields", "", "info");
  }
});

// DELETE BUSINESS HOUR
function removeBusinessHour(item_id) {
  const url = `/vendor/business-hours/delete/${item_id}`;
  console.log(url, item_id);
  fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      document.getElementById(`day-${data.id}`).remove();
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
}
