const searchInput = document.getElementById("product-search");

const productRows = document.querySelectorAll(".product-row");


searchInput.addEventListener("input", function () {

    const searchValue = searchInput.value
        .toLowerCase()
        .trim();


    productRows.forEach(function (row) {

        const rowText = row.textContent
            .toLowerCase();


        if (rowText.includes(searchValue)) {

            row.style.display = "";

        } else {

            row.style.display = "none";

        }

    });

});