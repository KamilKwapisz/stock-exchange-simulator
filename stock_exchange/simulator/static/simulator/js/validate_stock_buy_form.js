async function validateSubmit(form){
    let stocksNumber = document.getElementById("id_number").value;
    try {
        stocksNumber = parseInt(stocksNumber)
    } catch (error) {
        return false;
    }
    let price = {{ object.price }};
    let balance = {{ balance }};
    if (price * stocksNumber > balance) {
        return false;
    } else {
        return true;
    }
}