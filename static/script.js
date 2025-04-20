// static/script.js

const surnameInput = document.getElementById("surname");
const nameInput = document.getElementById("name");
const patronymicInput = document.getElementById("patronymic");

const genitiveOutput = document.getElementById("genitive_output");
const instrumentalOutput = document.getElementById("instrumental_output");

const crimeTypeSelect = document.getElementById("crime_type_select");
const crimeTypeCustom = document.getElementById("crime_type_custom");

const crimePlaceSelect = document.getElementById("crime_place_select");
const crimePlaceCustom = document.getElementById("crime_place_custom");

function updateNameInflections() {
  const surname = surnameInput.value.trim();
  const name = nameInput.value.trim();
  const patronymic = patronymicInput.value.trim();

  if (!surname || !name || !patronymic) {
    genitiveOutput.value = "";
    instrumentalOutput.value = "";
    return;
  }

  const url = `/inflect?surname=${encodeURIComponent(
    surname
  )}&name=${encodeURIComponent(name)}&patronymic=${encodeURIComponent(
    patronymic
  )}`;

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error(data.error);
      } else {
        genitiveOutput.value = data.genitive_variant;
        instrumentalOutput.value = data.instrumental_variant;
      }
    })
    .catch((err) => console.error("Помилка:", err));
}

function updateCrimeType() {
  if (crimeTypeSelect.value === "custom") {
    crimeTypeCustom.style.display = "block";
  } else {
    crimeTypeCustom.style.display = "none";
  }
}

function updateCrimePlace() {
  if (crimePlaceSelect.value === "custom") {
    crimePlaceCustom.style.display = "block";
  } else {
    crimePlaceCustom.style.display = "none";
  }
}

surnameInput.addEventListener("input", updateNameInflections);
nameInput.addEventListener("input", updateNameInflections);
patronymicInput.addEventListener("input", updateNameInflections);

crimeTypeSelect.addEventListener("change", updateCrimeType);
crimePlaceSelect.addEventListener("change", updateCrimePlace);
