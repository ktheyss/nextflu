---
---
var file_prefix = 'H1N1pdm_';
var dfreq_dn = 2;

var time_ticks = [2010, 2011, 2012, 2013, 2014, 2015];
var	time_window = 2.0;  // layer of one year that is considered current or active
var LBItau = 0.0005;
var LBItime_window = 0.5;
var freqdefault = "6b, 6c";

{%include_relative H1N1pdm_vaccines.js %}
