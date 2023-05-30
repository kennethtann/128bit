
document.getElementById("travelForm").addEventListener("submit", function(event) {
    event.preventDefault();
  
    const characterType = document.getElementById("characterType").value;
    const budget = document.getElementById("budget").value;
    const duration = parseInt(document.getElementById("duration").value);
  
    const recommendedCountry = recommendCountry(characterType, budget, duration);
    const activities = getCountryActivities(recommendedCountry);
    const visaRequirement = checkVisaRequirement(recommendedCountry, "Singapore");
    const itinerary = generateItinerary(activities, duration);
    const foods = getCountryFoods(recommendedCountry);
    const souvenirs = getCountrySouvenirs(recommendedCountry);
  
    const url = "recommendation.html" +
      "?country=" + encodeURIComponent(recommendedCountry) +
      "&activities=" + encodeURIComponent(JSON.stringify(activities)) +
      "&visaRequirement=" + encodeURIComponent(visaRequirement) +
      "&itinerary=" + encodeURIComponent(JSON.stringify(itinerary)) +
      "&foods=" + encodeURIComponent(JSON.stringify(foods)) +
      "&souvenirs=" + encodeURIComponent(JSON.stringify(souvenirs));
  
    const blackBackground = document.createElement("div");
    blackBackground.classList.add("black-background", "fade-in");
  
    const text = document.createElement("h2");
    text.textContent = "SPECIALLY CRAFTED FOR THE " + characterType.toUpperCase();
    text.style.fontSize = "2rem";
    text.style.fontWeight = "bold";
    text.style.color = "#fff";
    text.style.textAlign = "center";
    text.style.position = "absolute";
    text.style.top = "50%";
    text.style.left = "50%";
    text.style.transform = "translate(-50%, -50%)";
  
  
    blackBackground.appendChild(text);
    document.body.appendChild(blackBackground);
  
    setTimeout(function() {
      blackBackground.classList.add("fade-out");
      text.classList.add("fade-out");
  
      setTimeout(function() {
        window.location.href = url;
      }, 1000); // Redirect after fade-out animation completes
    }, 2500); // Fade out after 2 seconds
  });
  