const key = "a1a0faea3d4ff494cc5ee924959e25be";

function putData(data) {
    console.log("Dados recebidos:", data); // Para debug
    document.getElementById("cityName").textContent = data.name;
    document.getElementById("temperature").textContent = Math.floor(data.main.temp);
    document.getElementById("weatherDescription").textContent = data.weather[0].description;
    document.getElementById("humidityValue").textContent = data.main.humidity;
    document.getElementById("weatherIcon").src = `https://openweathermap.org/img/wn/${data.weather[0].icon}.png`;
}

async function searchCity(city) {
    try {
        const response = await fetch(
            `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${key}&lang=pt_br&units=metric`
        );
        
        if (!response.ok) throw new Error("Cidade não encontrada");
        const data = await response.json();
        putData(data);
        
    } catch (error) {
        console.error("Erro na busca:", error);
        alert("Erro ao buscar cidade. Verifique o nome e tente novamente.");
        // Reseta para os valores padrão
        document.getElementById("cityName").textContent = "São Paulo";
        document.getElementById("temperature").textContent = "21";
        document.getElementById("weatherDescription").textContent = "Nublado";
        document.getElementById("humidityValue").textContent = "76";
        document.getElementById("weatherIcon").src = "https://openweathermap.org/img/wn/04n.png";
    }
}

// Função chamada pelo botão de busca
function clickButton() {
    const city = document.getElementById("cityInput").value.trim();
    if (city) {
        searchCity(city);
    } else {
        alert("Por favor, digite o nome de uma cidade");
    }
}

// Permite buscar com Enter
document.getElementById("cityInput").addEventListener("keypress", function(event) {
    if (event.key === "Enter") clickButton();
});
