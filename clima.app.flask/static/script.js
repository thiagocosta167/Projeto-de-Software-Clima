const key = "a1a0faea3d4ff494cc5ee924959e25be";

function putData(data) {
  document.getElementById("cityName").textContent = data.name;
  document.getElementById("temperature").textContent = Math.floor(data.main.temp);
  document.getElementById("weatherDescription").textContent = data.weather[0].description;
  document.getElementById("humidityValue").textContent = data.main.humidity;
  document.getElementById("weatherIcon").src =
    `https://openweathermap.org/img/wn/${data.weather[0].icon}.png`;
}

async function searchCity(city, saveToHistory = true) {
  if (!city || city.trim() === "") return;

  try {
    const response = await fetch(
      `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&appid=${key}&lang=pt_br&units=metric`
    );

    if (!response.ok) throw new Error("Cidade não encontrada");

    const data = await response.json();
    putData(data);

    if (saveToHistory && city.trim().toLowerCase() !== "são paulo") {
      await fetch("/historico", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cidade: city })
      });
    }
  } catch (error) {
    alert("Erro ao buscar cidade. Verifique o nome e tente novamente.");
  }
}

// Função de favoritar otimizada
async function handleFavorite() {
  const favoriteBtn = document.getElementById("favoriteBtn");
  const cidadeAtual = document.getElementById("cityName").textContent.trim();

  // Validação melhorada para São Paulo
  const isSaoPauloDefault = cidadeAtual === "São Paulo" &&
    !document.getElementById("cityInput").value.trim() &&
    !window.location.search.includes("cidade");

  if (isSaoPauloDefault) {
    alert("Busque uma cidade válida primeiro!");
    return;
  }

  favoriteBtn.disabled = true;

  try {
    const response = await fetch("/favoritar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cidade: cidadeAtual })
    });

    const result = await response.json();
    alert(result.erro || result.mensagem);
  } catch (error) {
    alert("Erro na conexão com o servidor");
  } finally {
    favoriteBtn.disabled = false;
  }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  // Busca inicial
  const urlParams = new URLSearchParams(window.location.search);
  const cityFromUrl = urlParams.get('cidade');
  searchCity(cityFromUrl || "São Paulo", false);

  // Favoritar (com prevenção de duplicação)
  const favoriteBtn = document.getElementById("favoriteBtn");
  if (favoriteBtn) {
    favoriteBtn.addEventListener("click", handleFavorite);
  }

  // Busca
  document.getElementById("cityInput").addEventListener("keypress", e => {
    if (e.key === "Enter") searchCity(e.target.value.trim(), true);
  });

  document.querySelector(".button-search").addEventListener("click", () => {
    searchCity(document.getElementById("cityInput").value.trim(), true);
  });
});
