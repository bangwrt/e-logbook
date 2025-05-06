document.getElementById('searchInput').addEventListener('input', function () {
    const searchValue = this.value.toLowerCase();
    const tableRows = document.querySelectorAll('#dataTableBody tr');

    tableRows.forEach(row => {
        const id = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        const detail = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
        const note = row.querySelector('td:nth-child(4)').textContent.toLowerCase();
        const status = row.querySelector('td:nth-child(7)').textContent.toLowerCase();

        if (id.includes(searchValue) || detail.includes(searchValue) || note.includes(searchValue) || status.includes(searchValue)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});
