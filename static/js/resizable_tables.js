document.addEventListener('DOMContentLoaded', function() {
    const tables = document.querySelectorAll('table.resizable');

    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach(header => {
            const resizer = document.createElement('div');
            resizer.className = 'resizer';
            header.appendChild(resizer);

            let x = 0;
            let w = 0;

            const onMouseMove = function(e) {
                const dx = e.clientX - x;
                const newWidth = w + dx;
                header.style.width = `${newWidth}px`;
            };

            const onMouseUp = function() {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            };

            resizer.addEventListener('mousedown', function(e) {
                x = e.clientX;
                w = header.offsetWidth;
                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
            });
        });
    });
});

