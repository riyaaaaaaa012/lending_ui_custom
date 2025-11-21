// Reorder dashboard to show charts above number cards
(function() {
    let hasReordered = false;
    
    function reorderDashboard() {
        // Skip if already reordered
        if (hasReordered) {
            return true;
        }
        
        console.log('Attempting to reorder dashboard...');
        
        // Find the page content
        const pageContent = document.querySelector('.page-content');
        
        if (!pageContent) {
            console.log('Page content not found');
            return false;
        }
        
        // Find all widget groups
        const allWidgetGroups = pageContent.querySelectorAll('.widget-group');
        
        console.log('Found widget groups:', allWidgetGroups.length);
        
        if (allWidgetGroups.length < 2) {
            console.log('Not enough widget groups');
            return false;
        }
        
        let numberCardsGroup = null;
        let chartsGroup = null;
        
        // Check each group
        allWidgetGroups.forEach(function(group, index) {
            const numberCards = group.querySelectorAll('.number-widget-box');
            const charts = group.querySelectorAll('.dashboard-widget-box');
            
            console.log('Group', index, '- Number cards:', numberCards.length, '| Charts:', charts.length);
            
            if (numberCards.length > 0) {
                numberCardsGroup = group;
            }
            if (charts.length > 0) {
                chartsGroup = group;
            }
        });
        
        // Reorder if both groups exist
        if (numberCardsGroup && chartsGroup) {
            const parent = numberCardsGroup.parentNode;
            
            // Get positions
            const cardsPosition = Array.from(parent.children).indexOf(numberCardsGroup);
            const chartsPosition = Array.from(parent.children).indexOf(chartsGroup);
            
            console.log('Positions - Cards:', cardsPosition, '| Charts:', chartsPosition);
            
            // If cards come before charts, swap them
            if (cardsPosition < chartsPosition) {
                parent.insertBefore(chartsGroup, numberCardsGroup);
                console.log('✓ SUCCESS! Charts moved above cards');
                hasReordered = true;
                return true;
            } else {
                console.log('Charts already above cards');
                hasReordered = true;
                return true;
            }
        } else {
            console.log('Waiting for widgets to load...');
            return false;
        }
    }
    
    // Create a MutationObserver to watch for widget additions
    function observeDashboard() {
        const pageContent = document.querySelector('.page-content');
        
        if (!pageContent) {
            setTimeout(observeDashboard, 500);
            return;
        }
        
        console.log('Setting up dashboard observer...');
        
        const observer = new MutationObserver(function(mutations) {
            // Check if widgets were added
            let widgetsAdded = false;
            
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        if (node.classList && (node.classList.contains('widget-group') || 
                            node.querySelector && node.querySelector('.widget-group'))) {
                            widgetsAdded = true;
                        }
                    }
                });
            });
            
            if (widgetsAdded) {
                console.log('Widgets detected, attempting reorder...');
                setTimeout(reorderDashboard, 200);
            }
        });
        
        // Start observing
        observer.observe(pageContent, {
            childList: true,
            subtree: true
        });
        
        console.log('Dashboard observer active');
    }
    
    // Try immediate reordering
    setTimeout(reorderDashboard, 500);
    setTimeout(reorderDashboard, 1000);
    setTimeout(reorderDashboard, 2000);
    setTimeout(reorderDashboard, 3000);
    
    // Set up observer
    observeDashboard();
    
    // Listen for Frappe page changes
    if (window.frappe) {
        frappe.router.on('change', function() {
            console.log('Page changed, resetting reorder flag...');
            hasReordered = false;
            setTimeout(reorderDashboard, 500);
            setTimeout(reorderDashboard, 1500);
        });
    }
})();