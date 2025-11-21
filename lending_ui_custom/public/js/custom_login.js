// Replace login page logo with custom logo
(function() {
    function replaceLoginLogo() {
        // Find the Frappe logo image
        const frappeLogos = document.querySelectorAll('img.app-logo, img[src*="frappe"], .page-card-head img');
        
        frappeLogos.forEach(function(logo) {
            // Replace the src with our custom logo
            logo.src = '/assets/lending_ui_custom/images/custom_logo.svg';
            logo.style.maxHeight = '80px';
            logo.style.width = 'auto';
        });
    }
    
    // Run immediately
    replaceLoginLogo();
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', replaceLoginLogo);
    }
    
    // Run multiple times to catch any delayed loading
    setTimeout(replaceLoginLogo, 100);
    setTimeout(replaceLoginLogo, 300);
    setTimeout(replaceLoginLogo, 500);
    setTimeout(replaceLoginLogo, 1000);
})();