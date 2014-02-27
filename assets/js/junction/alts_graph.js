/**
 * Created by HansiHE on 2/27/14.
 */

Molecular.register("alts_graph", function() {
    $(function() {
        var svg = d3.select("#graph")
            .attr("viewBox", "0 0 600 400")
            .attr("preserveAspectRatio", "xMidYMid meet");

        var username_input_field = $("#username-input");
        var username_input_button = $("#username-button");
        username_input_button.click(function() {
            loadPlayer(username_input_field.val());
        });

        var loadedPlayers = [];

        var loadPlayer = function(username) {
            var origin = username.toLowerCase();

            if ($.inArray(origin, loadedPlayers)) {
                return
            }
            loadedPlayers.push(origin);

            $.ajax({
                dataType: "json",
                url: "/api/anathema/alts",
                data: {"username": username_input_field.val()},
                success: function(data) {
                    var alt_list = data.alts;

                    if(findNode(origin) == null) {
                        addNode(origin);
                    }

                    for(var i=0; i<alt_list.length; i++) {
                        var alt = alt_list[i];
                        var name = alt.alt.toLowerCase();
                        if (findNode(name) == null) {
                            addNode(name);
                        }
                        if (findLink(origin, name) == null && findLink(name, origin) == null) {
                            addLink(origin, name);
                        }
                    }

                    update();
                }
            })
        };

        var force = d3.layout.force()
            .gravity(.05)
            .distance(100)
            .charge(-100)
            .size([600, 400]);
        var nodes = force.nodes(),
            links = force.links();

        var addNode = function (id) {
            nodes.push({"id":id});
        };

        var findNode = function(id) {
            for (var i in nodes) {
                if (nodes[i]["id"] === id) {
                    return nodes[i]
                }
            }
        };

        var findNodeIndex = function(id) {
            for (var i in nodes){
                if (nodes[i]["id"] === id) {
                    return i;
                }
            }
        };

        var removeNode = function (id) {
            var i = 0;
            var n = findNode(id);
            while (i < links.length) {
                if ((links[i]['source'] == n)||(links[i]['target'] == n)) {
                    links.splice(i,1);
                }
                else i++;
            }
            nodes.splice(findNodeIndex(id),1);
        };

        var addLink = function (source, target) {
            links.push({"source":findNode(source),"target":findNode(target)});
        };

        var findLink = function (source, target) {
            for (var i in links) {
                if (links[i]["source"]["id"] === source && links[i]["target"]["id"] === target) {
                    return links[i];
                }
            }
        }

        var update = function () {
            var link = svg.selectAll("line.link")
                .data(links, function(d) { return d.source.id + "-" + d.target.id });

            link.enter().insert("line")
                .attr("class", "link")
                .attr("style", "stroke:rgb(150,150,150); stroke-width:2;");

            link.exit().remove();


            var node = svg.selectAll("g.node")
                .data(nodes, function(d) { return d.id; });

            var nodeEnter = node.enter().append("g")
                .attr("class", "node")
                .call(force.drag)
                .on("click", function(d) {
                    loadPlayer(d.id)
                });
            nodeEnter.append("circle")
                .attr("r", 5)
                .style("fill", "#357a00" );
            nodeEnter.append("text")
                .attr("class", "player-node-name")
                .attr("dx", "8px")
                .attr("dy", "0.35em")
                .text(function(d) { return d.id });


            node.exit().remove();

            force.on("tick", function() {
                link.attr("x1", function(d) { return d.source.x; })
                    .attr("y1", function(d) { return d.source.y; })
                    .attr("x2", function(d) { return d.target.x; })
                    .attr("y2", function(d) { return d.target.y; });

                node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
            });

            force.start();
        };

        force.start();

    });
});