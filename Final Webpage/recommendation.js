document.addEventListener("DOMContentLoaded", function (event) {
    const queryParams = decodeQueryParams(window.location.href);
    const recommendedCountry = queryParams.country;
    const visaRequirement = queryParams.visaRequirement;
    const itinerary = JSON.parse(queryParams.itinerary);
    const foods = JSON.parse(queryParams.foods);
    const souvenirs = JSON.parse(queryParams.souvenirs);

    document.getElementById("recommendedCountry").textContent = "Recommended Country: " + recommendedCountry;
    document.getElementById("visaRequirement").textContent = visaRequirement;

    const itineraryTable = document.getElementById("itineraryTable");
    itineraryTable.innerHTML = `
      <thead>
        <tr>
          <th>Day</th>
          <th>Activity</th>
        </tr>
      </thead>
      <tbody>
        ${itinerary.map((day, index) => `<tr><td>${index + 1}</td><td>${day.replace(/Day \d+: /, "")}</td></tr>`).join("")}
      </tbody>
    `;

    const foodsList = document.getElementById("foodsList");
    foodsList.innerHTML = foods.map(food => `<li>${food}</li>`).join("");

    const souvenirsList = document.getElementById("souvenirsList");
    souvenirsList.innerHTML = souvenirs.map(souvenir => `<li>${souvenir}</li>`).join("");
  });