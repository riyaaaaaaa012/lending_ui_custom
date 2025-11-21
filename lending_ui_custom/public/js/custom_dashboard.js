// Hide widget spacer elements - CORRECT CLASS
(function() {
    function hideWidgetSpacers() {
        // Target elements with class "widget spacer" (two separate classes)
        const spacers = document.querySelectorAll('.widget.spacer');
        
        spacers.forEach(function(spacer) {
            spacer.style.display = 'none';
            spacer.style.height = '0';
            spacer.style.margin = '0';
            spacer.style.padding = '0';
        });
    }
    
    // Run when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hideWidgetSpacers);
    } else {
        hideWidgetSpacers();
    }
    
    // Run multiple times to catch dynamic content
    setTimeout(hideWidgetSpacers, 300);
    setTimeout(hideWidgetSpacers, 800);
    setTimeout(hideWidgetSpacers, 1500);
})();