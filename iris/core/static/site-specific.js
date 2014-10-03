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
    $('.delete').click(function() {
        return confirm("Do you really want to delete it ?");
    });

    $('select[multiple=multiple]').multiSelect();
});
