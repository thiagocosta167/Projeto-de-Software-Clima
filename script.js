

const key = "a1a0faea3d4ff494cc5ee924959e25be"

function putData(data) {
    console.log(data)

    document.querySelector(".city").innerHTML = "Tempo em " + data.name

    //Arredondar a temperatura 
    document.querySelector(".temp").innerHTML = Math.floor(data.main.temp) + "°C"

    document.querySelector(".climate-text").innerHTML = data.weather[0].description

    document.querySelector(".humidity").innerHTML = "Umidade: " + data.main.humidity + "%"

    document.querySelector(".climate-img").src = `https://openweathermap.org/img/wn/${data.weather[0].icon}.png`

}


async function searchCity(city) {

    //Mudar para português as informações
    //Mudar a temperatura para graus celsius
    const data = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${key}&lang=pt_br&units=metric`).then(Response => Response.json())

    putData(data)

}

function clickButton() {
    const city = document.querySelector(".placeholder-city").value


    searchCity(city)

}