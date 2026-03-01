const priceTiers = {
  low: 550,
  high: 750,
  extraHigh: 950,
  urgent: 1200,
};

const formatDate = new Intl.DateTimeFormat("no-NO", {
  weekday: "short",
  day: "2-digit",
  month: "2-digit",
});

function renderCalendar(days = 30) {
  const calendar = document.getElementById("calendar");
  calendar.innerHTML = "";

  const now = new Date();
  for (let i = 0; i < days; i += 1) {
    const date = new Date(now);
    date.setDate(now.getDate() + i);

    const dayCard = document.createElement("article");
    dayCard.className = "day";
    dayCard.innerHTML = `
      <div class="date">${formatDate.format(date)}</div>
      <div class="slot">Ledig: 15:00–23:00</div>
    `;

    calendar.appendChild(dayCard);
  }
}

function validateStartTime(startDate) {
  if (startDate.getHours() < 15) {
    return "Oppdrag må starte kl. 15:00 eller senere.";
  }
  return null;
}

function getHourlyRate(hoursAhead) {
  const daysAhead = hoursAhead / 24;

  if (daysAhead >= 14) {
    return { rate: priceTiers.low, label: "Lav pris (14+ dager i forveien)" };
  }

  if (hoursAhead >= 24) {
    return { rate: priceTiers.high, label: "Høy pris (1–13 dager i forveien)" };
  }

  if (hoursAhead >= 1) {
    return { rate: priceTiers.extraHigh, label: "Ekstra høy pris (1–23 timer i forveien)" };
  }

  return { rate: priceTiers.urgent, label: "Akuttpris (under 1 time i forveien)" };
}

function setupForm() {
  const form = document.getElementById("booking-form");
  const result = document.getElementById("result");

  const now = new Date();
  now.setMinutes(0, 0, 0);
  document.getElementById("start").value = new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000)
    .toISOString()
    .slice(0, 16);

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const startRaw = formData.get("start");
    const duration = Number(formData.get("duration"));

    const startDate = new Date(startRaw);
    const currentDate = new Date();

    if (Number.isNaN(startDate.getTime())) {
      result.textContent = "Velg en gyldig starttid.";
      return;
    }

    if (startDate <= currentDate) {
      result.textContent = "Starttid må være i fremtiden.";
      return;
    }

    const timeValidationError = validateStartTime(startDate);
    if (timeValidationError) {
      result.textContent = timeValidationError;
      return;
    }

    const hoursAhead = (startDate - currentDate) / (1000 * 60 * 60);
    const { rate, label } = getHourlyRate(hoursAhead);
    const total = rate * duration;

    result.innerHTML = `
      <strong>${label}</strong><br>
      Timepris: ${rate} kr/time<br>
      Estimert total for ${duration} timer: <strong>${total.toLocaleString("no-NO")} kr</strong>
    `;
  });
}

renderCalendar();
setupForm();
