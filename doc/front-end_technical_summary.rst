front-end Technical summary
===========================
here is tecnical summary about developing in front-end.

work flow tools
---------------
we need to create a directory structure at the beginning of development, download library or framework and build dist directory when deploying the project. we choose the yeoman_ to do the above work.

yeoman
~~~~~~
yeoman is comprised of three tools: yo_, bower_, grunt_. For installation and usage information, refer to yeoman_.

yo
##
yo scaffolds out a new application, writing your Grunt configuration and pulling in relevant Grunt tasks and Bower dependencies that you might need for your build.

Bower
#####
Bower is used for dependency management, so that you no longer have to manually download and manage your scripts.

Grunt
#####
Grunt is used to build, preview and test your project, developer can customize design tasks to testing and build packages.

Tips
####
here are small useful tips in developing with yeoman.

* yo can help us set up directory of webapp, it can also generate directory of other development-patterns, like backbone, angular, express, etc. You can search generators by `npm search yeoman-generator` and install them.
* bower not only can fetch library from github, but also can fetch a library from a specified path. like `bower install ~/workspace/myPackage`.
* When generating the directory, yo writes a standard Gruntfile which can be used as basis by developers. Note: Developers can also write their own Gruntfile from scratch.

Common Libraries
----------------
here are libraries and frameworks used in front-end development.

jQuery
~~~~~~
It makes things like HTML document traversal as well as making the manipulation, event handling, animation, and Ajax much simpler with an easy-to-use API that works across a multitude of browsers.

jquery provides three useful tools:

* selector, used as css selector, we can use `$` to choose a DOM(Document Object Model) element and generate a jquery object like: `$("#domId")`.
* event handler, jquery can bind some event listener and callback function to a DOM element. like: `$("button").on("click", function(e){alert("hello!");})`
* ajax, jquery provides many friendly API to handle ajax, like: `$.ajax`, `$.get`, `$.post`.

For more information, refer to jquery_.

Underscore
~~~~~~~~~~
Underscore.js is a utility-belt library for JavaScript that provides support for the usual functional suspects (each, map, reduce, filter...) without extending any core JavaScript objects.

underscore provides a lot of usful functions:

* handle of collection or array like: `each`, `zip`...
* Judge type of object like: `isEmpty`, `isNaN`...
* tools, like: `random`, `template`...

For more information, refer to underscore.js_.

Backbone
~~~~~~~~
A famous front-end MVC framework well designd for developing single-page application.

Backbone.js gives structure to web applications by providing models with key-value binding and custom events, collections with a rich API of enumerable functions, views with declarative event handling, and connects it all to your existing API over a RESTful JSON interface.

Backbone provides a router module to handle the callback method when the hash part of the url is changed. like "http://example.com/#user/0001".

Backbone.js depends on underscore.js and jquery(ajax).

For more information, refer to backbone_.

There are more front-end MVC framework, like: ember.js_, angular_, here is a website for comparison of various MVC-frameworks: todomvc_.

Bootstrap
~~~~~~~~~
A powerful UI framework that helps set up beautiful web page with ease.

Bootstrap provides many practical tools:

* Grid system, it is used for creating page layouts through a series of rows and columns that house your content.
* CSS classes, Global CSS settings, fundamental HTML elements styled and enhanced with extensible classes.
* Components, over a dozen reusable components built to provide iconography, dropdowns, navigation, alerts, popovers, and much more.
* Javascript plugin, bring Bootstrap's components to life with over a dozen custom jQuery plugins. Easily include them all, or one by one.

For more information, refer to Bootstrap_.

Highcharts
~~~~~~~~~~
Highcharts is a charting library written in pure HTML5/JavaScript, offering intuitive, interactive charts to your web site or web application. Highcharts currently supports line, spline, area, areaspline, column, bar, pie, scatter, angular gauges, arearange, areasplinerange, columnrange, bubble, box plot, error bars, funnel, waterfall and polar chart types. For more infomation, refer to Highcharts_.

there is a brother of highcharts named "Highstock". Highstock lets you create stock or general timeline charts in pure JavaScript, including sophisticated navigation options like a small navigator series, preset date ranges, date picker, scrolling and panning. For more information, refer to Highstock_.

Highcharts is powerful, but it is heavy at the same time. So sometimes we can choose other light-weight chart libraries, like jqPlot_ and ichartjs_.

Templates
---------
Javascript template-angine can build template to HTML DOM element with data. It is partical and high-performanced in development of RIA(rich Internet Application).

Here are frequently used template framework:

* Handlebars_ provides the power necessary to let you build semantic templates effectively with no frustration.
* Mustache_, famous Logic-less templates.
* EJS_.

.. _yeoman: http://yeoman.io/
.. _yo: https://github.com/yeoman/yo
.. _bower: http://bower.io/
.. _grunt: http://gruntjs.com/
.. _jquery: http://jquery.com/
.. _underscore.js: http://underscorejs.org/
.. _backbone: http://backbonejs.org/
.. _ember.js: http://emberjs.com/
.. _angular: http://angularjs.org/
.. _todomvc: http://todomvc.com/
.. _bootstrap: http://getbootstrap.com/
.. _handlebars: http://handlebarsjs.com/
.. _mustache: http://mustache.github.io/
.. _ejs: http://embeddedjs.com/
.. _Highcharts: http://www.highcharts.com/products/highcharts
.. _Highstock: http://www.highcharts.com/products/highstock
.. _jqPlot: http://www.jqplot.com/
.. _ichartjs: http://www.ichartjs.com/
