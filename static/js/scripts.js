$(document).ready(function() {
    if ($.fn.DataTable) {
        if (!$.fn.DataTable.isDataTable('.datatable')) { 
            $('.datatable').DataTable({
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.5/i18n/pt-BR.json'
                },
                pageLength: 10
            });
        }
    }
});
