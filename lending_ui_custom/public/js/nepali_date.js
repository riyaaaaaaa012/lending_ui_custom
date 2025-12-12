// Display BS dates alongside AD dates in Frappe forms
// Includes clickable Nepali calendar picker

frappe.provide("frappe.nepali_date");

frappe.nepali_date = {
    // BS month names in Nepali
    bs_month_names: [
        'बैशाख', 'जेष्ठ', 'आषाढ', 'श्रावण', 'भाद्र', 'आश्विन',
        'कार्तिक', 'मंसिर', 'पौष', 'माघ', 'फाल्गुन', 'चैत्र'
    ],
    
    bs_month_names_en: [
        'Baisakh', 'Jestha', 'Ashadh', 'Shrawan', 'Bhadra', 'Ashwin',
        'Kartik', 'Mangsir', 'Poush', 'Magh', 'Falgun', 'Chaitra'
    ],
    
    // BS year data - days in each month
    bs_data: {
        2080: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
        2081: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
        2082: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
        2083: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
        2084: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
        2085: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
        2086: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
    },

    // Accurate AD to BS conversion
    ad_to_bs: function(ad_date) {
        if (!ad_date) return '';
        
        try {
            let parts = ad_date.split('-');
            let year = parseInt(parts[0]);
            let month = parseInt(parts[1]);
            let day = parseInt(parts[2]);
            
            return this.convertADtoBS(year, month, day);
        } catch(e) {
            console.error('Error converting date:', e);
            return '';
        }
    },
    
    // BS to AD conversion
    bs_to_ad: function(bs_year, bs_month, bs_day) {
        try {
            // Reference date: 2025-04-14 = 2082-01-01
            const ref_ad = new Date(2025, 3, 14); // April 14, 2025
            const ref_bs = { year: 2082, month: 1, day: 1 };
            
            let days_diff = 0;
            
            // Calculate days from reference BS date
            if (bs_year > ref_bs.year || (bs_year === ref_bs.year && bs_month > ref_bs.month)) {
                // Forward calculation
                let y = ref_bs.year;
                let m = ref_bs.month;
                
                while (y < bs_year || (y === bs_year && m < bs_month)) {
                    days_diff += this.bs_data[y][m - 1];
                    m++;
                    if (m > 12) {
                        m = 1;
                        y++;
                    }
                }
                days_diff += bs_day - ref_bs.day;
            } else {
                // Backward calculation
                let y = ref_bs.year;
                let m = ref_bs.month;
                
                while (y > bs_year || (y === bs_year && m > bs_month)) {
                    m--;
                    if (m < 1) {
                        m = 12;
                        y--;
                    }
                    days_diff -= this.bs_data[y][m - 1];
                }
                days_diff += bs_day - ref_bs.day;
            }
            
            // Add days to reference AD date
            let ad_date = new Date(ref_ad);
            ad_date.setDate(ad_date.getDate() + days_diff);
            
            let year = ad_date.getFullYear();
            let month = String(ad_date.getMonth() + 1).padStart(2, '0');
            let day = String(ad_date.getDate()).padStart(2, '0');
            
            return `${year}-${month}-${day}`;
        } catch(e) {
            console.error('Error converting BS to AD:', e);
            return null;
        }
    },
    
    // AD to BS conversion
    convertADtoBS: function(yy, mm, dd) {
        const ref_ad = { year: 2025, month: 4, day: 14 };
        const ref_bs = { year: 2082, month: 1, day: 1 };
        
        let ad_date = new Date(yy, mm - 1, dd);
        let ref_date = new Date(ref_ad.year, ref_ad.month - 1, ref_ad.day);
        let diff_days = Math.floor((ad_date - ref_date) / (1000 * 60 * 60 * 24));
        
        let bs_year = ref_bs.year;
        let bs_month = ref_bs.month;
        let bs_day = ref_bs.day + diff_days;
        
        while (bs_day > (this.bs_data[bs_year] ? this.bs_data[bs_year][bs_month - 1] : 30)) {
            if (this.bs_data[bs_year] && this.bs_data[bs_year][bs_month - 1]) {
                bs_day -= this.bs_data[bs_year][bs_month - 1];
            } else {
                bs_day -= 30;
            }
            bs_month++;
            
            if (bs_month > 12) {
                bs_month = 1;
                bs_year++;
            }
        }
        
        while (bs_day < 1) {
            bs_month--;
            if (bs_month < 1) {
                bs_month = 12;
                bs_year--;
            }
            
            if (this.bs_data[bs_year] && this.bs_data[bs_year][bs_month - 1]) {
                bs_day += this.bs_data[bs_year][bs_month - 1];
            } else {
                bs_day += 30;
            }
        }
        
        return `${bs_year}-${String(bs_month).padStart(2, '0')}-${String(bs_day).padStart(2, '0')}`;
    },
    
    // Show BS calendar picker
    show_bs_calendar: function(frm, fieldname, current_bs_date) {
        let me = this;
        let bs_parts = current_bs_date.split('-');
        let current_year = parseInt(bs_parts[0]);
        let current_month = parseInt(bs_parts[1]);
        let current_day = parseInt(bs_parts[2]);
        
        let dialog = new frappe.ui.Dialog({
            title: __('Select Nepali Date (BS)'),
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'calendar_html',
                }
            ],
            primary_action_label: __('Close'),
            primary_action: function() {
                dialog.hide();
            }
        });
        
        dialog.show();
        
        // Render calendar
        me.render_bs_calendar(dialog, frm, fieldname, current_year, current_month, current_day);
    },
    
    // Render BS calendar
    render_bs_calendar: function(dialog, frm, fieldname, year, month, selected_day) {
        let me = this;
        let days_in_month = this.bs_data[year][month - 1];
        
        let html = `
            <div class="bs-calendar-container" style="font-family: 'Space Grotesk', sans-serif;">
                <div class="bs-calendar-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding: 10px; background: #003893; color: white; border-radius: 4px;">
                    <button class="btn btn-xs btn-default prev-month" style="color: white; border-color: white;">‹</button>
                    <div style="font-size: 16px; font-weight: 600;">
                        ${this.bs_month_names_en[month - 1]} ${year}
                        <div style="font-size: 12px; opacity: 0.9;">${this.bs_month_names[month - 1]} ${year}</div>
                    </div>
                    <button class="btn btn-xs btn-default next-month" style="color: white; border-color: white;">›</button>
                </div>
                
                <div class="bs-calendar-days" style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; text-align: center;">
                    <div style="font-weight: 600; color: #003893;">Sun</div>
                    <div style="font-weight: 600; color: #003893;">Mon</div>
                    <div style="font-weight: 600; color: #003893;">Tue</div>
                    <div style="font-weight: 600; color: #003893;">Wed</div>
                    <div style="font-weight: 600; color: #003893;">Thu</div>
                    <div style="font-weight: 600; color: #003893;">Fri</div>
                    <div style="font-weight: 600; color: #dc143c;">Sat</div>
        `;
        
        // Calculate first day of month
        let first_ad = me.bs_to_ad(year, month, 1);
        let first_day_obj = new Date(first_ad);
        let start_day = first_day_obj.getDay();
        
        // Empty cells for days before month starts
        for (let i = 0; i < start_day; i++) {
            html += '<div></div>';
        }
        
        // Days of the month
        for (let day = 1; day <= days_in_month; day++) {
            let is_selected = (day === selected_day);
            let style = `
                padding: 8px;
                cursor: pointer;
                border-radius: 4px;
                transition: all 0.2s;
                ${is_selected ? 'background: #003893; color: white; font-weight: 600;' : 'background: #f8f9fa;'}
            `;
            
            html += `<div class="bs-day" data-day="${day}" style="${style}">${day}</div>`;
        }
        
        html += `
                </div>
            </div>
        `;
        
        dialog.fields_dict.calendar_html.$wrapper.html(html);
        
        // Add event listeners
        dialog.fields_dict.calendar_html.$wrapper.find('.bs-day').on('click', function() {
            let selected_day = parseInt($(this).data('day'));
            let ad_date = me.bs_to_ad(year, month, selected_day);
            
            if (ad_date) {
                frm.set_value(fieldname, ad_date);
                dialog.hide();
            }
        });
        
        // Hover effect
        dialog.fields_dict.calendar_html.$wrapper.find('.bs-day').hover(
            function() {
                if (!$(this).css('background-color').includes('rgb(0, 56, 147)')) {
                    $(this).css({
                        'background': '#e6eef8',
                        'transform': 'scale(1.05)'
                    });
                }
            },
            function() {
                if (!$(this).css('background-color').includes('rgb(0, 56, 147)')) {
                    $(this).css({
                        'background': '#f8f9fa',
                        'transform': 'scale(1)'
                    });
                }
            }
        );
        
        // Month navigation
        dialog.fields_dict.calendar_html.$wrapper.find('.prev-month').on('click', function() {
            let new_month = month - 1;
            let new_year = year;
            if (new_month < 1) {
                new_month = 12;
                new_year--;
            }
            me.render_bs_calendar(dialog, frm, fieldname, new_year, new_month, selected_day);
        });
        
        dialog.fields_dict.calendar_html.$wrapper.find('.next-month').on('click', function() {
            let new_month = month + 1;
            let new_year = year;
            if (new_month > 12) {
                new_month = 1;
                new_year++;
            }
            me.render_bs_calendar(dialog, frm, fieldname, new_year, new_month, selected_day);
        });
    },
    
    // Add BS date display to a field
    add_bs_display: function(frm, fieldname) {
        let me = this;
        let field = frm.fields_dict[fieldname];
        if (!field) return;
        
        let $wrapper = field.$wrapper;
        if (!$wrapper) return;
        
        // Remove existing BS display
        $wrapper.find('.bs-date-display').remove();
        
        // Add BS date display element
        let $input = $wrapper.find('.control-input-wrapper');
        if ($input.length) {
            $input.append(`
                <div class="bs-date-display" style="
                    margin-top: 4px;
                    font-size: 12px;
                    color: #003893;
                    font-weight: 600;
                    cursor: pointer;
                    padding: 6px 10px;
                    background: #e6eef8;
                    border-radius: 4px;
                    border-left: 3px solid #003893;
                    transition: all 0.2s;
                " title="Click to open Nepali calendar">
                    <span class="bs-date-icon" style="margin-right: 6px;">📅</span>
                    <span class="bs-date-value"></span>
                    <span style="margin-left: 6px; font-size: 10px; opacity: 0.7;">▼</span>
                </div>
            `);
            
            // Click to open calendar
            $wrapper.find('.bs-date-display').on('click', function() {
                let ad_date = frm.doc[fieldname];
                if (ad_date) {
                    let bs_date = me.ad_to_bs(ad_date);
                    me.show_bs_calendar(frm, fieldname, bs_date);
                }
            });
            
            // Hover effect
            $wrapper.find('.bs-date-display').hover(
                function() {
                    $(this).css({
                        'background': '#003893',
                        'color': 'white',
                        'transform': 'translateY(-1px)',
                        'box-shadow': '0 2px 4px rgba(0,56,147,0.2)'
                    });
                },
                function() {
                    $(this).css({
                        'background': '#e6eef8',
                        'color': '#003893',
                        'transform': 'translateY(0)',
                        'box-shadow': 'none'
                    });
                }
            );
        }
        
        // Update BS date when AD date changes
        frm.fields_dict[fieldname].$input.on('change', function() {
            me.update_bs_display(frm, fieldname);
        });
        
        // Initial update
        this.update_bs_display(frm, fieldname);
    },
    
    // Update BS date display
    update_bs_display: function(frm, fieldname) {
        let ad_date = frm.doc[fieldname];
        let $display = frm.fields_dict[fieldname].$wrapper.find('.bs-date-value');
        
        if (ad_date && $display.length) {
            let bs_date = this.ad_to_bs(ad_date);
            let parts = bs_date.split('-');
            let month_name = this.bs_month_names_en[parseInt(parts[1]) - 1];
            $display.text(`${parts[2]} ${month_name} ${parts[0]} BS`);
            $display.parent().show();
        } else if ($display.length) {
            $display.parent().hide();
        }
    }
};

// Auto-add BS dates to common date fields
$(document).on('form-load', function(e, frm) {
    setTimeout(function() {
        let date_fields = ['posting_date', 'transaction_date', 'date', 
                          'from_date', 'to_date', 'start_date', 'end_date',
                          'disbursement_date', 'repayment_start_date'];
        
        date_fields.forEach(function(fieldname) {
            if (frm.fields_dict[fieldname]) {
                frappe.nepali_date.add_bs_display(frm, fieldname);
            }
        });
    }, 500);
});