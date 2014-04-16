/*
 * This file is part of IRIS: Infrastructure and Release Information System
 *
 *  Copyright (C) 2013 Intel Corporation
 *
 *  IRIS is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU General Public License
 *  version 2.0 as published by the Free Software Foundation.
 */

/*
 * This is the site specific JS file for the IRIS project.
 */

/**
 * Utility functions
 * */

var findIndex = function(list, value) {
    for (var index in list) {
        if (list[index] === value) {
            return index;
        }
    }

    return -1;
};

/**
 * Attaches filtering to the submissions summary table.
 */
$(document).ready(function() {
    if (!$('#submissions-summary').length) {
        return;
    }

    // Glyphicon constants for the BootStrap manipulation
    var up = 'glyphicon-chevron-up';
    var down = 'glyphicon-chevron-down';

    // Pagination is disabled before it's styled for BootStrap 3
    $('#submissions-summary').dataTable({
        'bPaginate': false,
    });

    // Hides datatable specific components; we have our own
    $('#submissions-summary_filter').addClass('hidden');
    $('#submissions-summary_info').addClass('hidden');

    // Global column filtering
    $('#global-filter').keyup(function() {
        $('#submissions-summary').dataTable().fnFilter(
            $('#global-filter').val(), null, true);
    });

    $('#product-filter').change(function(event) {
        var appUrl = '/app/submissions/summary/';
        productName = event.target.value;

        if (productName) {
            $(location).attr('href', appUrl + '?product=' + productName)
        } else {
            $(location).attr('href', appUrl)
        }
    });

    // Subfilters for each table column
    $('#name-filter').keyup(function() {
        $('#submissions-summary').dataTable().fnFilter(
            $('#name-filter').val(), 0, true);
    });

    $('#status-filter').change(function() {
        var key = $('#status-filter').val();
        var filtermap = {
            'Any status': '',
            'Pending': '^((?!(ACCEPTED|REJECTED)).)*$',
            'Testing': '.*TESTING.*',
            'Building': '.*BUILDING.*',
            'Accepted': 'ACCEPTED',
            'Failed': '.*FAIL.*',
            'Rejected': 'REJECTED',
        };

        $('#submissions-summary').dataTable().fnFilter(
            filtermap[key], 1, true);
    });

    $('#tree-submission-filter').keyup(function() {
        $('#submissions-summary').dataTable().fnFilter(
            $('#tree-submission-filter').val(), 2, true);
    });

    $('#created-date-filter').keyup(function() {
        $('#submissions-summary').dataTable().fnFilter(
            $('#created-date-filter').val(), 3, true);
    });

    $('#updated-date-filter').keyup(function() {
        $('#submissions-summary').dataTable().fnFilter(
            $('#updated-date-filter').val(), 4, true);
    });

    // React to dropdowns and sorting visually with chevrons
    $('#submissions-column-toggle').click(function() {
        var chevron = $('#submissions-filter-toggle-chevron');

        if (chevron.hasClass(down)) {
            chevron.removeClass(down).addClass(up);
        } else {
            chevron.removeClass(up).addClass(down);
        }
    });

    $('.sorter').click(function (event) {
        // Clear previous chevrons from column headers
        $('.sorter').children('span').removeClass(up).removeClass(down);

        // Add new chevrons to the table header that was clicked
        var th = $(event.target)
        var span = $(th.children('span'));

        if (span.hasClass('glyphicon')) {
            if (th.hasClass('sorting_asc')) {
                span.removeClass(up).addClass(down);
            } else if (th.hasClass('sorting_desc')) {
                span.removeClass(down).addClass(up);
            }
        }
    });

    // By default, hide accepted and rejected submissions from the user
    $('#submissions-summary').dataTable().fnFilter(
        '^((?!(ACCEPTED|REJECTED)).)*$', 1, true);

    // Sort the table by 'Updated' column
    $('#submissions-summary').dataTable().fnSort([[4, 'asc']]);
    $('.sorter:contains("Updated")').children('span').addClass(down);

    // Listener for submission selection checkboxes
});

/**
 * Submissions grouping page helpers
 */
$(document).ready(function() {
    var selectedSubmissions = []

    window.selectSubmission = function (id) {
        var i = findIndex(selectedSubmissions, id);

        if (i !== -1) {
            selectedSubmissions.splice(i, 1);

            if (selectedSubmissions.length === 0) {
                $('#create-group-submit').prop('disabled', true)
            }
        } else {
            selectedSubmissions.push(id);

            if (selectedSubmissions.length > 0) {
                $('#create-group-submit').prop('disabled', false)
            }
        }
    }

    var timeString = function () {
        var date = new Date();
        var Y = date.getUTCFullYear();
        var m = date.getUTCMonth() + 1;
        var d = date.getUTCDate();
        var H = date.getUTCHours();
        var M = date.getUTCMinutes();
        var S = date.getUTCSeconds();

        // Ensure we have padded values
        H = H < 10 ? '0' + H : H;
        S = S < 10 ? '0' + S : S;
        m = m < 10 ? '0' + m : m;

        return Y + m + d + '.' + H + M + S;
    };

    var setSubmitTime = function () {
        $('#submit-time').html(timeString());
    }

    setSubmitTime();
    window.setInterval(setSubmitTime, 1000);

    $('#create-group-submit').click(function (event) {
        // Don't go to URL; create an AJAX request instead
        event.preventDefault();

        // Get form fields, add submission list to them.
        var form = $('#create-group-form');
        var form_data = form.serializeArray();

        form_data.push({
            name: 'submissions',
            value: selectedSubmissions.join(',')
        });

        // Formulate an AJAX request, send asynchronously
        var request = {
            type: form.attr('method'),
            url: form.attr('action'),
            data: $.param(form_data),  // serialize form data for backend
            success: function(data) {
                $('.submissions-select').prop('checked', false);
                selectedSubmissions = [];
                var group_url = '/app/submissions/submissiongroups/';
                window.location = group_url + data.product;
            },
            error: function(data) {
                console.log('Failed at creating a new submission group');
                console.log('Sent data: ', JSON.stringify(form_data));
            }
        };

        $.ajax(request);
    });
});
