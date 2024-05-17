$(document).ready(function(){
    $("#search, #filter, #status-filter, #invoice-filter").on("change keyup", function() {
        var searchValue = $("#search").val().toLowerCase();
        var filterValue = $("#filter").val();
        var statusFilterValue = $("#status-filter").val();
        var invoiceFilterValue = $("#invoice-filter").val();

        $("#card-container .card").filter(function() {
            var textMatches = $(this).text().toLowerCase().indexOf(searchValue) > -1;
            var filterMatches = filterValue ? $(this).find('p:contains("Comercial:")').text().split(':')[1].trim() === filterValue : true;
            var statusFilterMatches = statusFilterValue ? $(this).find('p:contains("Status:")').text().split(':')[1].trim() === statusFilterValue : true;
            var invoiceFilterMatches = invoiceFilterValue ? $(this).find('p:contains("Tipo de Fatura:")').text().split(':')[1].trim() === invoiceFilterValue : true;
            $(this).toggle(textMatches && filterMatches && statusFilterMatches && invoiceFilterMatches);
        });
    });
});