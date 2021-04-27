var openregisterLocationPicker = require("govuk-country-and-territory-autocomplete");

openregisterLocationPicker({
  selectElement: document.getElementById("country-picker"),
  url: "/country/location-autocomplete-graph.json",
  defaultValue: "",
  displayMenu: "overlay",
});

var input = document.querySelector("#country-picker");
input.setAttribute("role", "combobox");
input.setAttribute("aria-describedby", "country-picker__assistiveHint");

var wrapper = document.getElementsByClassName("autocomplete__wrapper")[0];
var hint = document.getElementById("country-picker__assistiveHint");
wrapper.appendChild(hint);
