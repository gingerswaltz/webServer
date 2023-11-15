function updateChart() {
    var selectedPanel = document.getElementById('solarPanelSelect').value;
    if (selectedPanel) {
        // AJAX call to fetch data for the selected solar panel
        fetch(`/get-characteristics-data/${selectedPanel}`)
            .then(response => response.json())
            .then(data => {
                // Assuming 'data' is the characteristics data for the selected panel
                var ctx = document.getElementById('solarPanelChart').getContext('2d');
                var solarPanelChart = new Chart(ctx, {
var ctx = document.getElementById('generatedPowerChart-{{ solar_panel.installation_number }}').getContext('2d');
        var generatedPowerChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: {{ dashboard_data[solar_panel].chart_data.labels | safe }},
                datasets: [{
                    label: 'Generated Power',
                    data: {{ dashboard_data[solar_panel].chart_data.generated_power_data | safe }},
                    backgroundColor: 'rgba(0, 123, 255, 0.5)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    });
});
}
}