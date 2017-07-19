window.onload = function () {
    var ctx = document.getElementById('myChart');

    var myChart = new Chart(ctx,
    {
        type: 'scatter',
        data: {
            datasets: [ddd, eee]
        },
    })
}