document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("upload-form");
    const formCard = document.getElementById("form-card");
    const resultSection = document.getElementById("result-section");
    const resultsTable = document.getElementById("results-table");
    const errorSection = document.getElementById("error-section");
    const errorMessage = document.getElementById("error-message");
    const loadingSpinner = document.getElementById("loading-spinner");
    const backButton = document.getElementById("back-button");

    form.addEventListener("submit", async function(e) {
        e.preventDefault();

        hideSections();
        loadingSpinner.classList.remove("d-none");

        const fileInput = document.getElementById("file");
        const nameColumnInput = document.getElementById("name-column");
        const dateColumnInput = document.getElementById("date-column");

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        formData.append("name_column", nameColumnInput.value.trim());
        formData.append("date_column", dateColumnInput.value.trim());

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            loadingSpinner.classList.add("d-none");

            if (response.ok) {
                formCard.style.display = "none";
                showResults(data);
            } else {
                showError(data.error || "A apărut o eroare necunoscută.");
            }
        } catch (error) {
            loadingSpinner.classList.add("d-none");
            showError("Nu s-a putut conecta la server.");
        }
    });

    function hideSections() {
        resultSection.classList.add("d-none");
        errorSection.classList.add("d-none");
        errorMessage.textContent = "";
        loadingSpinner.classList.add("d-none");
    }

    function showResults(data) {
        if (!data.length) {
            showError("Nu există date expirate sau aproape expirate.");
            return;
        }

        resultSection.classList.remove("d-none");

        let tableHTML = `
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>Nume</th>
                        <th>Data Expirării</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.forEach(item => {
            tableHTML += `
                <tr>
                    <td>${item.name}</td>
                    <td>${item.date}</td>
                    <td>${item.status}</td>
                </tr>
            `;
        });

        tableHTML += `
                </tbody>
            </table>
        `;

        resultsTable.innerHTML = tableHTML;
    }

    function showError(message) {
        errorSection.classList.remove("d-none");
        errorMessage.textContent = message;
    }

    backButton.addEventListener("click", function() {
        window.location.href = "/";
    });
});
