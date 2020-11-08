[![Build Status](https://travis-ci.com/ladybug-tools/ladybug-grasshopper.svg?branch=master)](https://travis-ci.com/ladybug-tools/ladybug-grasshopper)

[![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# ladybug-grasshopper

:beetle: :green_book: Ladybug plugin for Grasshopper (aka. ladybug[+])

This repository contains all Grasshopper components for the ladybug plugin.
The package includes both the userobjects (`.ghuser`) and the Python source (`.py`).
Note that this library only possesses the Grasshopper components and, in order to
run the plugin, the core libraries must be installed in a way that
they can be found by Rhino (see dependencies).

## Dependencies

The ladybug-grasshopper plugin has the following dependencies (other than Rhino/Grasshopper):

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-comfort](https://github.com/ladybug-tools/ladybug-comfort)
* [ladybug-rhino](https://github.com/ladybug-tools/ladybug-rhino)

## Installation

See the [Wiki of the lbt-grasshopper repository](https://github.com/ladybug-tools/lbt-grasshopper/wiki)
for the installation instructions for the entire Ladybug Tools Grasshopper plugin
(including this repository).
