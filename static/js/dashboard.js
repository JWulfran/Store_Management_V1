// ==========================================
// DASHBOARD CHARTS
// ==========================================

// Data received from Django

const monthLabels = JSON.parse(
    document.getElementById("month-labels").textContent
);

const monthlySales = JSON.parse(
    document.getElementById("monthly-sales").textContent
);

const monthlyPurchases = JSON.parse(
    document.getElementById("monthly-purchases").textContent
);


// ==========================================
// SALES CHART
// ==========================================

const salesCtx = document.getElementById("salesChart");

new Chart(salesCtx, {
    type: "line",

    data: {
        labels: monthLabels,

        datasets: [{
            label: "Ventes ($)",
            data: monthlySales,
            borderColor: "#2563eb",
            backgroundColor: "rgba(37, 99, 235, 0.1)",
            fill: true,
            tension: 0.3
        }]
    },

    options: {
        responsive: true,
        maintainAspectRatio: false,

        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});


// ==========================================
// PURCHASES CHART
// ==========================================

const purchasesCtx = document.getElementById(
    "purchasesChart"
);

new Chart(purchasesCtx, {
    type: "bar",

    data: {
        labels: monthLabels,

        datasets: [{
            label: "Achats ($)",
            data: monthlyPurchases,
            backgroundColor: "#0d9488",
            borderRadius: 5
        }]
    },

    options: {
        responsive: true,
        maintainAspectRatio: false,

        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});