[![Build Status](https://travis-ci.org/ladybug-tools/ladybug-grasshopper.svg?branch=master)](https://travis-ci.org/ladybug-tools/ladybug-grasshopper)

[![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# ladybug-grasshopper
:beetle: :green_book: Ladybug plugin for Grasshopper (aka. ladybug[+])

This repository contains all Grasshopper components for the dragonfly plugin.
The package includes both the userobjects (`.ghuser`) and the Python source (`.py`).
Note that this library only possesses the Grasshopper components and, in order to
run the plugin, the core libraries must be installed (see dependencies).

## Dependencies

The honeybee-grasshopper plugin has the following dependencies (other than Rhino/Grasshopper):

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-dotnet](https://github.com/ladybug-tools/ladybug-dotnet)
* [ladybug-rhino](https://github.com/ladybug-tools/ladybug-rhino)
