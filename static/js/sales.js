document.addEventListener("DOMContentLoaded", () => {

    const productSelect = document.getElementById("id_product");
    const quantityInput = document.getElementById("id_quantity");

    const priceDisplay = document.getElementById("unit-price");
    const stockDisplay = document.getElementById("available-stock");
    const totalDisplay = document.getElementById("sale-total");

    const productDataElement = document.getElementById("product-data");

    if (!productDataElement) {
        return;
    }

    const products = JSON.parse(
        productDataElement.textContent
    );


    function updateSaleInformation() {

        const productId = productSelect.value;

        const product = products[productId];

        if (!product) {

            priceDisplay.textContent = "0.00 $";
            stockDisplay.textContent = "-";
            totalDisplay.textContent = "0.00 $";

            return;
        }


        const price = parseFloat(product.price);

        const stock = parseInt(product.stock);

        const quantity = parseInt(
            quantityInput.value
        ) || 0;


        priceDisplay.textContent =
            `${price.toFixed(2)} $`;

        stockDisplay.textContent =
            stock;

        quantityInput.max = stock;


        const total = price * quantity;

        totalDisplay.textContent =
            `${total.toFixed(2)} $`;
    }


    productSelect.addEventListener(
        "change",
        updateSaleInformation
    );


    quantityInput.addEventListener(
        "input",
        updateSaleInformation
    );


    updateSaleInformation();

});