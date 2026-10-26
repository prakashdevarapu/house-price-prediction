/**
 * House Price Prediction - Dashboard JavaScript Controller
 * Handles AJAX form submission, client-side validation, session stats updates,
 * and Chart.js trend visualization.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const form = document.getElementById("prediction-form");
    const btnPredict = document.getElementById("btn-predict");
    const btnSample = document.getElementById("btn-sample");
    const formErrorBanner = document.getElementById("form-error-banner");

    // Result panel elements
    const emptyState = document.getElementById("result-empty-state");
    const contentState = document.getElementById("result-content-state");
    const resultPriceInr = document.getElementById("result-price-inr");
    const resultPriceCompact = document.getElementById("result-price-compact");
    const resFeatArea = document.getElementById("res-feat-area");
    const resFeatBed = document.getElementById("res-feat-bed");
    const resFeatBath = document.getElementById("res-feat-bath");
    const resFeatFloors = document.getElementById("res-feat-floors");
    const resFeatAge = document.getElementById("res-feat-age");
    const resFeatRate = document.getElementById("res-feat-rate");

    // Stat card elements
    const statTotalCount = document.getElementById("stat-total-count");
    const statLatestPrice = document.getElementById("stat-latest-price");
    const statLatestSub = document.getElementById("stat-latest-sub");
    const statAvgPrice = document.getElementById("stat-avg-price");
    const statAvgSub = document.getElementById("stat-avg-sub");
    const historyBadge = document.getElementById("history-badge");

    // Form inputs
    const inputs = {
        area_sqft: document.getElementById("area_sqft"),
        bedrooms: document.getElementById("bedrooms"),
        bathrooms: document.getElementById("bathrooms"),
        floors: document.getElementById("floors"),
        age_years: document.getElementById("age_years"),
    };

    // Limits & validation specs
    const validationRules = {
        area_sqft: { min: 100, max: 25000, label: "Built-up Area", integer: false },
        bedrooms: { min: 1, max: 20, label: "Bedrooms", integer: true },
        bathrooms: { min: 1, max: 15, label: "Bathrooms", integer: true },
        floors: { min: 1, max: 10, label: "Floors", integer: true },
        age_years: { min: 0, max: 120, label: "Property Age", integer: false },
    };

    // Setup Chart.js
    let historyChart = null;
    initPredictionChart();

    // Event Listeners
    form.addEventListener("submit", handleFormSubmit);
    btnSample.addEventListener("click", fillSampleData);

    // Clear individual error message on input change
    Object.keys(inputs).forEach((key) => {
        inputs[key].addEventListener("input", () => {
            clearFieldError(key);
            hideBannerError();
        });
    });

    /**
     * Pre-populates realistic sample values for quick evaluation.
     */
    function fillSampleData() {
        const samples = [
            { area: 1850, bed: 3, bath: 2, floors: 2, age: 3 },
            { area: 1200, bed: 2, bath: 2, floors: 1, age: 5 },
            { area: 2600, bed: 4, bath: 3, floors: 2, age: 1.5 },
            { area: 950, bed: 2, bath: 1, floors: 1, age: 8 },
        ];
        const pick = samples[Math.floor(Math.random() * samples.length)];

        inputs.area_sqft.value = pick.area;
        inputs.bedrooms.value = pick.bed;
        inputs.bathrooms.value = pick.bath;
        inputs.floors.value = pick.floors;
        inputs.age_years.value = pick.age;

        Object.keys(inputs).forEach(clearFieldError);
        hideBannerError();
    }

    /**
     * Frontend validation checking bounds, emptiness, and integers.
     */
    function validateForm() {
        let isValid = true;
        hideBannerError();

        for (const [key, field] of Object.entries(inputs)) {
            clearFieldError(key);
            const valStr = field.value.trim();
            const rules = validationRules[key];

            if (valStr === "") {
                setFieldError(key, `${rules.label} is required.`);
                isValid = false;
                continue;
            }

            const num = Number(valStr);
            if (isNaN(num)) {
                setFieldError(key, `Please enter a valid numeric value.`);
                isValid = false;
                continue;
            }

            if (rules.integer && !Number.isInteger(num)) {
                setFieldError(key, `${rules.label} must be a whole number.`);
                isValid = false;
                continue;
            }

            if (num < rules.min) {
                setFieldError(key, `Must be at least ${rules.min}.`);
                isValid = false;
                continue;
            }

            if (num > rules.max) {
                setFieldError(key, `Cannot exceed ${rules.max}.`);
                isValid = false;
                continue;
            }
        }

        return isValid;
    }

    function setFieldError(fieldKey, message) {
        const input = inputs[fieldKey];
        input.classList.add("is-invalid");
        const errorSpan = document.getElementById(`error-${fieldKey}`);
        if (errorSpan) {
            errorSpan.textContent = message;
        }
    }

    function clearFieldError(fieldKey) {
        const input = inputs[fieldKey];
        input.classList.remove("is-invalid");
        const errorSpan = document.getElementById(`error-${fieldKey}`);
        if (errorSpan) {
            errorSpan.textContent = "";
        }
    }

    function showBannerError(msg) {
        formErrorBanner.textContent = msg;
        formErrorBanner.style.display = "block";
    }

    function hideBannerError() {
        formErrorBanner.style.display = "none";
        formErrorBanner.textContent = "";
    }

    /**
     * Form submission handler.
     */
    async function handleFormSubmit(e) {
        e.preventDefault();

        if (!validateForm()) {
            showBannerError("Please correct the highlighted errors above.");
            return;
        }

        const payload = {
            area_sqft: parseFloat(inputs.area_sqft.value),
            bedrooms: parseInt(inputs.bedrooms.value, 10),
            bathrooms: parseInt(inputs.bathrooms.value, 10),
            floors: parseInt(inputs.floors.value, 10),
            age_years: parseFloat(inputs.age_years.value),
        };

        setLoading(true);

        try {
            const response = await fetch("/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body: JSON.stringify(payload),
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                const errorMsg = result.error || "Failed to calculate prediction.";
                showBannerError(errorMsg);
                return;
            }

            // Update UI with predictions
            renderPredictionResult(result.data.prediction, payload);
            renderStats(result.data.stats);
            updateChart(result.data.stats.history);

        } catch (err) {
            console.error("Prediction error:", err);
            showBannerError("Network error. Unable to reach the prediction server.");
        } finally {
            setLoading(false);
        }
    }

    function setLoading(isLoading) {
        const btnText = btnPredict.querySelector(".btn-text");
        const btnLoader = btnPredict.querySelector(".btn-loader");

        if (isLoading) {
            btnPredict.disabled = true;
            btnText.style.display = "none";
            btnLoader.style.display = "inline-flex";
        } else {
            btnPredict.disabled = false;
            btnText.style.display = "inline";
            btnLoader.style.display = "none";
        }
    }

    /**
     * Renders predicted valuation in the Results panel.
     */
    function renderPredictionResult(pred, inputs) {
        emptyState.style.display = "none";
        contentState.style.display = "flex";

        resultPriceInr.textContent = pred.formatted_price;
        resultPriceCompact.textContent = pred.compact_price;

        resFeatArea.textContent = `${inputs.area_sqft.toLocaleString()} sq ft`;
        resFeatBed.textContent = `${inputs.bedrooms} BHK`;
        resFeatBath.textContent = `${inputs.bathrooms} Baths`;
        resFeatFloors.textContent = `${inputs.floors} Storey`;
        resFeatAge.textContent = `${inputs.age_years} yrs old`;

        // Derived rate per sq ft
        const ratePerSqft = Math.round(pred.raw_price / inputs.area_sqft);
        resFeatRate.textContent = `₹${ratePerSqft.toLocaleString()} / sqft`;
    }

    /**
     * Updates top statistic cards.
     */
    function renderStats(stats) {
        statTotalCount.textContent = stats.total_predictions;
        statLatestPrice.textContent = stats.latest_price;
        statLatestSub.textContent = stats.latest_price_compact;
        statAvgPrice.textContent = stats.average_price;
        statAvgSub.textContent = stats.average_price_compact;

        if (historyBadge) {
            historyBadge.textContent = `${stats.total_predictions} Predictions`;
        }
    }

    /**
     * Initialize Chart.js prediction history line graph.
     */
    function initPredictionChart() {
        const ctx = document.getElementById("predictionChart");
        if (!ctx) return;

        const initialHistory = window.INITIAL_HISTORY || [];
        const labels = initialHistory.map((_, idx) => `#${idx + 1}`);
        const dataValues = initialHistory.map((item) => item.raw_price / 100000); // in Lakhs for readability

        if (typeof Chart === "undefined") {
            console.warn("Chart.js failed to load. Chart will be disabled.");
            return;
        }

        historyChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels.length ? labels : ["Waiting for first prediction..."],
                datasets: [
                    {
                        label: "Estimated Value (₹ in Lakhs)",
                        data: dataValues.length ? dataValues : [0],
                        borderColor: "#10b981",
                        backgroundColor: "rgba(16, 185, 129, 0.08)",
                        borderWidth: 2.5,
                        pointBackgroundColor: "#0f172a",
                        pointBorderColor: "#10b981",
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        tension: 0.35,
                        fill: true,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: "top",
                        labels: {
                            font: { family: "Inter", size: 12 },
                            color: "#475569",
                        },
                    },
                    tooltip: {
                        backgroundColor: "#0f172a",
                        titleFont: { family: "Inter", size: 12 },
                        bodyFont: { family: "Inter", size: 13, weight: "bold" },
                        callbacks: {
                            label: function (context) {
                                const lakhVal = context.parsed.y;
                                return ` Estimated: ₹${lakhVal.toFixed(2)} Lakhs`;
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        grid: { color: "#f1f5f9" },
                        ticks: { color: "#64748b", font: { family: "Inter" } },
                    },
                    y: {
                        grid: { color: "#f1f5f9" },
                        ticks: {
                            color: "#64748b",
                            font: { family: "Inter" },
                            callback: function (value) {
                                return `₹${value} L`;
                            },
                        },
                    },
                },
            },
        });
    }

    /**
     * Updates prediction line chart with fresh session points.
     */
    function updateChart(history) {
        if (!historyChart || !history) return;

        const labels = history.map((_, idx) => `#${idx + 1}`);
        const valuesInLakhs = history.map((item) => (item.raw_price / 100000).toFixed(2));

        historyChart.data.labels = labels;
        historyChart.data.datasets[0].data = valuesInLakhs;
        historyChart.update();
    }
});
