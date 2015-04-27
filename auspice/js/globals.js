var regions = ["Africa", "SouthAmerica", "WestAsia", "Oceania", "Europe", "JapanKorea", "NorthAmerica", "SoutheastAsia", "SouthAsia", "China"]
var restrictTo = "all";

var cladeToSeq = {}

var globalDate = new Date();

var nodes, tips, rootNode, links, vaccines, sera;

function treePlotHeight(width) {
	return 400 + 0.35*width;
}
var containerWidth = parseInt(d3.select(".treeplot-container").style("width"), 10);
var treeWidth = containerWidth, treeHeight;
treeHeight = treePlotHeight(treeWidth);
var tree = d3.layout.tree()
	.size([treeHeight, treeWidth]);


var treeplot = d3.select("#treeplot")
	.attr("width", treeWidth)
	.attr("height", treeHeight);

var legend = d3.select("#legend")
	.attr("width", 280)
	.attr("height", 100);

var colorBy = document.getElementById("coloring").value;
var colorScale;
var time_step;


d3.json("/data/" + file_prefix + "meta.json", function(error, json) {
    if (error) return console.warn(error);
    d3.select("#updated").text(json['updated']);
    commit_id = json['commit'];
    short_id = commit_id.substring(0, 6);   
    d3.select("#commit")
        .append("a")
        .attr("href", "http://github.com/blab/nextflu/commit/" + commit_id)
        .text(short_id);

});