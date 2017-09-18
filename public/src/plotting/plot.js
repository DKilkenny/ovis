var createPlot = function (container) {
    var search;
    var curData = [];
    var searchString = '';
    var element = container.getElement()[0].lastChild;
    var searchElement = container.getElement()[0].firstChild;
    var selectPicker = container.getElement()[0].children[1];
    searchElement.style.width = (container.width - 20).toString() + 'px';
    searchElement.style.height = '15px';
    searchElement.style.marginTop = '20px';
    element.style.width = container.width.toString() + 'px';
    element.style.height = (container.height - 60).toString() + 'px';

    //Set up the basic plot
    if (element != null) {
        Plotly.plot(element, [{
            x: [1, 2, 3, 4, 5],
            y: [0, 0, 0, 0, 0]
        }],
            { margin: { t: 0 } }
        );
    }

    /**
     * Function which is called when the window is resized.
     * Resets the dimensions for plotly
     */
    var resize = function () {
        //Set element's dimensions
        element.style.width = container.width.toString() + 'px';
        element.style.height = (container.height - 60).toString() + 'px';
        searchElement.style.width = (container.width - 20).toString() + 'px';

        //Set up plotly's dimensions
        Plotly.relayout(element, {
            width: container.width,
            height: container.height - 60
        });
    };

    /**
     * Function which sets plot's data. Searches through to determine
     * which values to show, then updates plotly
     * 
     * @param {[Object]} dat 
     */
    var setData = function (dat) {
        curData = [];

        //Place everything in the data array
        for (var i = 0; i < dat.length; ++i) {
            var indexOfIterType = getIndexOfIterType(dat[i]['iteration']);
            if (indexOfIterType == -1) {
                curData.push([dat[i]]);
            }
            else {
                curData[indexOfIterType].push(dat[i]);
            }
        }

        //Determine which data set to plot by default
        var largestCount = -1;
        var index = -1;
        for (var i = 0; i < curData.length; ++i) {
            if (curData[i].length > largestCount) {
                largestCount = curData.length;
                index = i;
            }
        }

        setNewPlotData(index);
    };

    /**
     * Called when the selectPicker is clicked. Updates plot with new data
     */
    var selectClicked = function () {
        var index = Number(selectPicker.value);
        setNewPlotData(index);
    }
    selectPicker.onchange = selectClicked;

    /**
     * Sorts and formats data at the given index of curData, then 
     * plots it
     * 
     * @param {int} index 
     */
    var setNewPlotData = function (index) {
        //Sort the data to be plotted
        curData[index].sort(compareIterations);

        //Set up data for plotting
        var finalData = getData(index);

        //Set the precision of the data
        for (var j = 0; j < finalData['inputs_outputs'].length; ++j) {
            for (var i = 0; i < finalData['inputs_outputs'][j].y.length; ++i) {
                var val = finalData['inputs_outputs'][j].y[i];
                val = Math.round(val * 100000000) / 100000000;
                finalData['inputs_outputs'][j].y[i] = val;
            }
        }
        for (var j = 0; j < finalData['residuals'].length; ++j) {
            for (var i = 0; i < finalData['residuals'][j].y.length; ++i) {
                var val = finalData['residuals'][j].y[i];
                val = Math.round(val * 100000000) / 100000000;
                finalData['residuals'][j].y[i] = val;
            }
        }
        //Set up the layout
        var layout = {
            title: searchString,
            xaxis: {
                title: 'Global Counter',
                // dtick: 1
            },
            yaxis: {
                title: 'Value'
            }
        }

        //Add residuals to inputs_outputs
        for(var i = 0; i < finalData['residuals'].length; ++i) {
            finalData['inputs_outputs'].push(finalData['residuals'][i])
        }

        //plot it
        Plotly.newPlot(element, finalData['inputs_outputs'], layout);

        //Update the select picker
        while (selectPicker.options.length > 0) {
            selectPicker.remove(0);
        }
        for (var i = index; i < curData.length; ++i) {
            var t = curData[i][0];
            selectPicker.options.add(new Option(getIterationName(t), i));
        }

        for (var i = 0; i < index; ++i) {
            var t = curData[i][0];
            selectPicker.options.add(new Option(getIterationName(t), i));
        }
    }

    /**
     * Pulls out the data at the given index from curData and returns
     * it in a format that's friendly for Plotly
     * 
     * @param {int} index
     * @return {Object}
     */
    var getData = function (index) {
        var finalData = {
            'residuals': [],
            'inputs_outputs': []
        };
        var got_first_in_outs = false;
        var got_first_resids = false;
        for (var i = 0; i < curData[index].length; ++i) {
            for (var j = 0; j < curData[index][i]['values'].length; ++j) {
                if (curData[index][i]['values'][0].hasOwnProperty('length')) {
                    for (var k = 0; k < curData[index][i]['values'][0].length; ++k) {
                        if ((curData[index][i]['type'] !== 'residual' && !got_first_in_outs) || (curData[index][i]['type'] === 'residual' && !got_first_resids)) {
                            if (curData[index][i]['type'] !== 'residual') {
                                got_first_in_outs = true;
                                finalData['inputs_outputs'].push({
                                    x: [curData[index][i]['counter']],
                                    y: [curData[index][i]['values'][j][k]],
                                    name: '[0][0]'
                                });
                            }
                            else {
                                got_first_resids = true;
                                finalData['residuals'].push({
                                    x: [curData[index][i]['counter']],
                                    y: [curData[index][i]['values'][j][k]],
                                    name: 'Residuals [0][0]'
                                });
                            }
                        }
                        else {
                            if (curData[index][i]['type'] !== 'residual') {
                                var k_len = curData[index][i]['values'][0].length;
                                finalData['inputs_outputs'][k_len * j + k].x.push(curData[index][i]['counter']);
                                finalData['inputs_outputs'][k_len * j + k].y.push(curData[index][i]['values'][j][k]);
                                finalData['inputs_outputs'][k_len * j + k].name = '[' + j + '][' + k + ']';
                            }
                            else {
                                finalData['residuals'][k_len * j + k].x.push(curData[index][i]['counter']);
                                finalData['residuals'][k_len * j + k].y.push(curData[index][i]['values'][j][k]);
                                finalData['residuals'][k_len * j + k].name = 'Residuals [' + j + '][' + k + ']';
                            }
                        }
                    }
                }
                else {
                    if ((curData[index][i]['type'] !== 'residual' && !got_first_in_outs) || (curData[index][i]['type'] === 'residual' && !got_first_resids)) {
                        if (curData[index][i]['type'] !== 'residual') {
                            got_first_in_outs = true;
                            finalData['inputs_outputs'].push({
                                x: [curData[index][i]['counter']],
                                y: [curData[index][i]['values'][j]],
                                name: 'Index 0'
                            });
                        }
                        else {
                            got_first_resids = true;
                            finalData['residuals'].push({
                                x: [curData[index][i]['counter']],
                                y: [curData[index][i]['values'][j]],
                                name: 'Residuals'
                            });
                        }
                    }
                    else {
                        if (curData[index][i]['type'] !== 'residual') {
                            finalData['inputs_outputs'][j].x.push(curData[index][i]['counter']);
                            finalData['inputs_outputs'][j].y.push(curData[index][i]['values'][j]);
                            finalData['inputs_outputs'][j].name = 'Index ' + j;
                        }
                        else {
                            finalData['residuals'][j].x.push(curData[index][i]['counter']);
                            finalData['residuals'][j].y.push(curData[index][i]['values'][j]);
                            finalData['residuals'][j].name = 'Residuals Index ' + j;
                        }
                    }
                }
            }
        }

        return finalData;
    }

    /**
     * Returns the iteration name, which is the sum of the names in the
     * iteration array.
     * 
     * @param {Iteration} iteration 
     * @return {String}
     */
    var getIterationName = function (iteration) {
        var s = "";
        if (iteration === null) return s;
        s += iteration['iteration'][0].name;
        for (var i = 1; i < iteration['iteration'].length; ++i) {
            s += '::' + iteration['iteration'][i].name;
        }
        return s;
    }

    /**
     * Compares two iterations by their counter. Returns
     *  1 if a > b, -1 if a < b, and 0 if they're equal.
     * 
     * @param {Iteration} a 
     * @param {Iteration} b 
     * @return {int}
     */
    var compareIterations = function (a, b) {
        if (a['counter'] > b['counter']) {
            return 1;
        }
        else if (b['counter'] > a['counter']) {
            return -1;
        }

        return 0;
    }

    /**
     * Checks to see if curData already has a similar iteration.
     * Algorithm:
     *  1. Check to see if there's anything in curData that has the same
     *      iteration length
     *  2. If something does, check to make sure the iteration names are the same
     *  3. If the names are the same, return the index
     *  4. Otherwise, return -1
     * 
     * @param {Object} iter 
     * @return {int}
     */
    var getIndexOfIterType = function (iter) {
        for (var i = 0; i < curData.length; ++i) {
            var tempIter = curData[i][0]['iteration'];
            var found = true;
            if (tempIter.length == iter.length) {
                for (var j = 0; j < tempIter.length; ++j) {
                    if (tempIter[j]['name'] != iter[j]['name']) {
                        found = false;
                        break;
                    }
                }

                if (found) {
                    return i;
                }
            }
        }

        return -1;
    };

    /**
     * Attempts to get the data with the given name and
     * plot it.
     * 
     * @param {string} name 
     */
    var handleSearch = function (name) {
        http.get('case/' + case_id + '/system_iterations/' + name, function (result) {
            result = JSON.parse(result);
            searchString = name;
            setData(result);
        });
    };

    //Get the variables
    http.get('case/' + case_id + '/variables', function (result) {
        result = JSON.parse(result);
        search = new Awesomplete(searchElement, { list: result });

        var randIndex = Math.floor(Math.random() * result.length);
        if (randIndex < result.length) {
            handleSearch(result[randIndex]);
        }
    });

    //Bind to search so that we grab data and update plot after searching
    Awesomplete.$.bind(searchElement, {
        "awesomplete-select": function (event) {
            handleSearch(event.text.value);
        }
    });

    //Set callback on resize
    container.on('resize', resize);
};
