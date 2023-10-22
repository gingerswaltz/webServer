document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('th a').forEach(function(columnHeader) {
        columnHeader.addEventListener('click', function(event) {
            event.preventDefault();
            const url = new URL(window.location.href);
            const sortColumn = this.getAttribute('data-column');
            const sortDirection = url.searchParams.get('sort_column') === sortColumn ? (url.searchParams.get('sort_direction') === 'asc' ? 'desc' : 'asc') : 'asc';
            url.searchParams.set('sort_column', sortColumn);
            url.searchParams.set('sort_direction', sortDirection);
            window.location.href = url;
        });
    });
});