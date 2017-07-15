window.onload = function () {
    var ctx = document.getElementById('myChart');
    var myChart = new Chart(ctx,
    {
        type: 'bar',
        data:
        {
            labels: dates,
            datasets:
            [
                {
                    type: 'bar',
                    label: "Visitor",
                    data: counts
                },
                {
                    type: 'line',
                    label: "Sales",
                    data: counts,
                }
            ]
        }
    })
}