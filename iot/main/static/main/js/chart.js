// Parse data for Chart.js
var ctx = document.getElementById('characteristicsChart').getContext('2d');
var dates = JSON.parse('{{ dates|safe }}');
var generatedPower = JSON.parse('{{ generated_power|safe }}');
var consumedPower = JSON.parse('{{ consumed_power|safe }}');

// Render Chart.js Line Chart
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: dates,
        datasets: [
            {
                label: 'Generated Power',
                data: generatedPower,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            },
            {
                label: 'Consumed Power',
                data: consumedPower,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }
        ]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});