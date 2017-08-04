"use strict";

/**
 * Class HTTP - allows user to contact the server for any HTTP requests
 */
function HTTP() {
    this.baseURL = 'http://openmdao.org/visualization/'
    
    /**
     * function get - performs HTTP GET request at given address (after prepending
     *  base URL) and calls the success or error callback
     * 
     * @param path - the URL excluding the base URL (which is automatically prepended)
     * @param success - the success callback. Should have one input, the response
     * @param error - the failure callback. Should have one input, the reason for error
     */
    this.get = function(path, success, error) {
        
        $.ajax({
            url: this.baseURL + path,
            type: 'GET',
            headers: {'token': 'squavy'},
            success: function(response) { success(response) }
        });
    };
};

var http = new HTTP();