const productSelect = document.getElementById("id_product");
const unitPriceInput = document.getElementById("id_unit_price");

const productPrices = JSON.parse(
    document.getElementById("product-prices").textContent
);

productSelect.addEventListener("change", function () {
    const productId = this.value;

    if (productId && productPrices[productId]) {
        unitPriceInput.value = productPrices[productId];
    } else {
        unitPriceInput.value = "";
    }
});