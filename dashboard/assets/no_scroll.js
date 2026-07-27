document.addEventListener('wheel', function(e) {
    if (document.activeElement && document.activeElement.type === 'number') {
        document.activeElement.blur();
    }
}, { passive: true });
