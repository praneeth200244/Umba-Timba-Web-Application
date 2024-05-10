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
