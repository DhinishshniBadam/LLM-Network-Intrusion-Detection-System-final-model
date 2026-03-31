async function predict(){

    const input = document.getElementById("inputData").value;

    let data;

    try{
        data = JSON.parse(input);
    }
    catch{
        alert("Enter valid JSON data");
        return;
    }

    const response = await fetch("http://127.0.0.1:8000/predict",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    document.getElementById("resultBox").classList.remove("hidden");
    document.getElementById("result").innerHTML =
    "Prediction: " + result.prediction + "<br>" +
    "Confidence: " + (result.confidence*100).toFixed(2) + "%<br>" +
    //"Risk Score: " + result.risk_score + "<br><br>" +
    "<b>" + result.alert + "</b>";
}