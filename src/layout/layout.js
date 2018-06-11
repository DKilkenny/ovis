'use strict';

const fs = require('fs');
const path = require('path');
const is = require('electron-is');

/**
 * Class Layout - Handles loading/saving/updating the layout
 */
function Layout() {
    // ******************* Local Variables ******************* //

    // The list of callbacks to get configs from plots
    // so that we can update their componentState on the server.
    // NOTE: It's the responsibility of the plot to add its callback via addPlotCallback.
    // Passing by reference does not work when passing around componentState, unfortunately
    let configCallbacks = [];
    let lastLayout = null;
    let myLayout = null;

    // Grab the ptn2 and plot HTML data
    let ptn2_loc = path.join(
        process.resourcesPath,
        'components/partition_tree_n2.html'
    );
    let plot_loc = path.join(process.resourcesPath, 'components/plot.html');
    if (is.dev()) {
        ptn2_loc = path.join(__dirname, 'components/partition_tree_n2.html');
        plot_loc = path.join(__dirname, 'components/plot.html');
    }
    let ptn2_file = fs.readFileSync(ptn2_loc);
    let plot_file = fs.readFileSync(plot_loc);

    /**
     * Constructor
     */
    function initialize() {
        //Create the initial golden layout dashboard
        server.getLayout(function(ret) {
            if (ret.length === 0) {
                myLayout = createLayout(config);
            } else {
                myLayout = createLayout(JSON.parse(ret[0]['layout']));
            }
        });

        ipc.getFilename(function(filename) {
            if (filename.length > 14) {
                filename = filename.substring(0, 14) + '...';
            }

            document.getElementById(
                'sidebarHeaderContent'
            ).innerHTML = filename;
            console.log(filename);
        });
    }

    // ******************* Public Methods ******************* //

    /**
     * Add the current plot to the config callback which requests
     * the plot's component state.
     *
     * @param {function} callback - function that returns plot component state
     */
    this.addPlotCallback = function(callback) {
        configCallbacks.push(callback);
    };

    /**
     * Saves the current layout to the server
     *
     * @param {*} lt
     */
    this.saveLayout = function(lt) {
        // If we're in tests, don't save the new layout
        if (process.env.RUNNING_IN_VIS_INDEX_TESTS) {
            return;
        }

        if (lt == null) {
            //when plots are trying to save, layout will be null
            lt = lastLayout;

            if (lastLayout == null) {
                return;
            }
        }

        lastLayout = lt;
        let state = lt.toConfig();
        let componentStates = getComponentStates();
        replaceComponentStates(state, componentStates);
        server.saveLayout(state, function() {});
    };

    /**
     * Adds another plot to the current dashboard or creates a new
     * dashboard if one does not exist.
     */
    this.addNewPlot = function() {
        if (myLayout.root !== null && myLayout.root.contentItems.length > 0) {
            myLayout.root.contentItems[0].addChild(getPlotConfig());
        } else {
            //Everything was deleted in the dashboard
            //Remove the previous layout
            let n = document.getElementById('goldenLayout');
            while (n.firstChild) {
                n.removeChild(n.firstChild);
            }

            //Configure new layout
            let newConfig = {
                content: [
                    {
                        type: 'row',
                        content: [getPlotConfig()]
                    }
                ]
            };
            myLayout = createLayout(newConfig);
        }
    };

    /**
     * Adds an N^2 diagram to the current dashboard or creaes a new
     * dashboard if one does not exist.
     */
    this.addNewN2 = function() {
        if (myLayout.root !== null && myLayout.root.contentItems.length > 0) {
            myLayout.root.contentItems[0].addChild(getN2Config());
        } else {
            //Remove the previous layout
            let n = document.getElementById('goldenLayout');
            while (n.firstChild) {
                n.removeChild(n.firstChild);
            }

            //Configure the new layout
            let newConfig = {
                content: [
                    {
                        type: 'row',
                        content: [getN2Config()]
                    }
                ]
            };
            myLayout = createLayout(newConfig);
        }
    };

    // ******************* Private Helper Methods ******************* //

    /**
     * Returns a random number between 0 and 100,000,000
     *
     * @returns {String} random number as string
     */
    function getRand() {
        return Math.floor(Math.random() * 100000000).toString();
    }

    /**
     * Get a plot configuration
     */
    function getPlotConfig() {
        //Golden Layout configuration for plots
        let plotConfig = {
            type: 'component',
            componentName: 'Variable vs. Iterations',
            componentState: {
                label: getRand(),
                localscaleXVal: false,
                localscaleYVal: false,
                stackedPlotVal: false,
                selectedDesignVariables: [],
                selectedConstraints: [],
                selectedObjectives: [],
                selectedSysincludes: [],
                variableIndices: []
            }
        };
        return plotConfig;
    }

    /**
     * Get an N2 configuration
     */
    function getN2Config() {
        //Golden Layout configuration for N^2
        let n2Config = {
            type: 'component',
            componentName: 'Partition Tree and N<sup>2</sup>',
            componentState: { label: getRand() }
        };
        return n2Config;
    }

    /**
     * Creates a new Golden Layout based on the configuration passed
     * to it and returns the GoldenLayout.
     *
     * @param {*} newConfig
     */
    function createLayout(newConfig) {
        let lt = new GoldenLayout(newConfig);
        registerN2(lt);
        registerPlot(lt);
        lt.container = '#goldenLayout';
        lt._isFullPage = true;
        lt.init();
        lt.on('stateChanged', function() {
            layout.saveLayout(lt);
        });
        return lt;
    }

    /**
     * Registers the N^2 Golden Layout configuration so that N^2 diagrams
     * may be added
     *
     * @param {*} lt
     */
    function registerN2(lt) {
        lt.registerComponent('Partition Tree and N<sup>2</sup>', function(
            container,
            componentState
        ) {
            let resourceLocation = process.resourcesPath;
            container.getElement().html(ptn2_file.toString());

            // ptn2 is a global variable found in ptn2.js
            ptn2.initializeTree(container);

            // Disable the Add N2 button because you can't have multiple N2
            document.getElementById('addN2Button').disabled = true;

            // If we close the container, re-enable the Add N2 button
            container.on('destroy', function(container) {
                document.getElementById('addN2Button').disabled = false;
            });
        });
    }

    /**
     * Registers the Plot Golden Layout configuration s othat plots may be
     * added
     *
     * @param {*} lt
     */
    function registerPlot(lt) {
        lt.registerComponent('Variable vs. Iterations', function(
            container,
            componentState
        ) {
            // Add the plot component to the container
            container.getElement().html(plot_file.toString());

            // Global function found in plot.js
            new Plot(container, componentState);
        });
    }

    /**
     * Goes through, finds, and replaces all component states that are
     * in the component states map. Used by saveLayout
     *
     * NOTE: recursive method (could be replaced with a stack)
     *
     * @param {*} state
     * @param {*} componentStatesMap
     */
    function replaceComponentStates(state, componentStatesMap) {
        if (state.hasOwnProperty('componentState')) {
            let label = state.componentState.label;
            if (Number(label) in componentStatesMap) {
                state.componentState = componentStatesMap[label];
            }
        }

        if (state.hasOwnProperty('content')) {
            for (let i = 0; i < state.content.length; ++i) {
                replaceComponentStates(state.content[i], componentStatesMap);
            }
        }
    }

    /**
     * Grabs all componentStates from the configCallbacks array.
     * Returns a map from label to componentState
     */
    function getComponentStates() {
        let ret = {};
        for (let i = 0; i < configCallbacks.length; ++i) {
            let config = configCallbacks[i]();
            ret[config['label']] = config;
        }

        return ret;
    }

    //Initial configuration.
    // 2 plots next to an N^2
    let config = {
        content: [
            {
                type: 'row',
                content: [
                    getN2Config(),
                    {
                        type: 'column',
                        content: [getPlotConfig(), getPlotConfig()]
                    }
                ]
            }
        ]
    };

    initialize();
}

// Arbitrary case ID at the moment because it isn't used by the server
// at this time (vestigial).
var case_id = '1885148375';
const layout = new Layout();
