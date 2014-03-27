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
 * Attaches filtering to the submissions summary table.
 */
$(document).ready(function() {
    // Pagination is disabled before it's styled for BootStrap 3
    $('#submissions-summary').dataTable({
        'bPaginate': false,
    });

    // Hides datatable specific components; we have our own
    $('#submissions-summary_filter').addClass('hidden');
    $('#submissions-summary_info').addClass('hidden');

    $("#date-filter").keyup(function() {
        $('#submissions-summary').dataTable().fnFilter(
            $("#date-filter").val(), 0, true);
    });

    $("#name-filter").keyup(function() {
        $('#submissions-summary').dataTable().fnFilter(
            $("#name-filter").val(), 1, true);
    });

    $("#tree-submission-filter").keyup(function() {
        $('#submissions-summary').dataTable().fnFilter(
            $("#tree-submission-filter").val(), 2, true);
    });

    $("#status-filter").change(function() {
        var key = $("#status-filter").val();
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
            filtermap[key], 3, true);
    });
});
