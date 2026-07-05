// frontend/assets/js/weather.js

const API_BASE = `${CONFIG.API_URL}/api/weather`; // uses backend URL from config.js
const tokenKey = CONFIG.STORAGE_KEYS.TOKEN;

function getToken() {
  return localStorage.getItem(tokenKey);
}

function showMessage(text, isError = false) {
  const el = document.getElementById('message');
  el.textContent = text;
  el.className = isError ? 'error' : 'info';
  if (!text) el.className = '';
}

function showCurrent(data) {
  document.getElementById('locationName').textContent = data.location || 'Unknown';
  document.getElementById('temp').textContent = `${data.temperature} °C`;
  document.getElementById('feels').textContent = `${data.feels_like} °C`;
  document.getElementById('humidity').textContent = `${data.humidity} %`;
  document.getElementById('pressure').textContent = `${data.pressure} hPa`;
  document.getElementById('wind').textContent = `${data.wind_speed} m/s`;
  document.getElementById('clouds').textContent = `${data.clouds} %`;
  document.getElementById('description').textContent = data.description || '';
  document.getElementById('currentWeather').classList.remove('hidden');
}

function showForecast(list) {
  const container = document.getElementById('forecastList');
  container.innerHTML = '';
  list.forEach(item => {
    const card = document.createElement('div');
    card.className = 'forecast-item';
    card.innerHTML = `
      <div class="time">${item.time}</div>
      <div class="temp">${item.temperature} °C</div>
      <div class="desc">${item.description}</div>
      <div class="wind">Wind: ${item.wind_speed} m/s</div>
      <div class="hum">Humidity: ${item.humidity}%</div>
    `;
    container.appendChild(card);
  });
  document.getElementById('forecast').classList.remove('hidden');
}

async function fetchCurrent(params) {
  const token = getToken();
  if (!token) {
    showMessage('You must be logged in to view weather. Please login first.', true);
    return;
  }

  const url = new URL(`${API_BASE}/current`, window.location.origin);
  Object.keys(params).forEach(k => url.searchParams.append(k, params[k]));

  try {
    showMessage('Loading current weather...');
    const res = await fetch(url.toString(), {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const json = await res.json();
    if (res.ok && json.success) {
      showMessage('');
      showCurrent(json.weather);
    } else {
      showMessage(json.message || 'Unable to fetch current weather', true);
    }
  } catch (err) {
    showMessage('Network error: ' + err.message, true);
  }
}

async function fetchForecast(params) {
  const token = getToken();
  if (!token) return;

  const url = new URL(`${API_BASE}/forecast`, window.location.origin);
  Object.keys(params).forEach(k => url.searchParams.append(k, params[k]));

  try {
    showMessage('Loading forecast...');
    const res = await fetch(url.toString(), {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const json = await res.json();
    if (res.ok && json.success) {
      showMessage('');
      showForecast(json.forecast);
    } else {
      showMessage(json.message || 'Unable to fetch forecast', true);
    }
  } catch (err) {
    showMessage('Network error: ' + err.message, true);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const searchBtn = document.getElementById('searchBtn');
  const geoBtn = document.getElementById('geoBtn');
  const cityInput = document.getElementById('cityInput');

  searchBtn.addEventListener('click', () => {
    const city = cityInput.value.trim();
    if (!city) {
      showMessage('Please enter a city name', true);
      return;
    }
    fetchCurrent({ city });
    fetchForecast({ city });
  });

  geoBtn.addEventListener('click', () => {
    if (!navigator.geolocation) {
      showMessage('Geolocation not supported by your browser', true);
      return;
    }
    showMessage('Getting your location...');
    navigator.geolocation.getCurrentPosition(
      pos => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        fetchCurrent({ lat, lon });
        fetchForecast({ lat, lon });
      },
      err => {
        showMessage('Unable to get location: ' + err.message, true);
      },
      { timeout: 10000 }
    );
  });

  // Optional: if you want to auto-load weather for a saved city in config.js
  if (window.DEFAULT_CITY) {
    cityInput.value = window.DEFAULT_CITY;
    // do not auto-fetch; let user click
  }
});