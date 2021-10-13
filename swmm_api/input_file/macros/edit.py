from numpy import interp, mean, ceil
from networkx import DiGraph

from .collection import nodes_dict, links_dict, subcachtment_nodes_dict
from .graph import next_links_labels, previous_links, previous_links_labels, links_connected
from .macros import calc_slope
from .. import section_labels as sec
from ..section_lists import NODE_SECTIONS, LINK_SECTIONS
from ..sections import Tag, DryWeatherFlow, Junction, Coordinate, Conduit, Loss, Vertices, EvaporationSection
from ... import SwmmInput


def delete_node(inp: SwmmInput, node_label, graph: DiGraph = None, alt_node=None):
    """
    delete node in inp data

    Notes:
        works inplace

    Args:
        inp (SwmmInput): inp data
        node_label (str): label of node to delete
        graph (DiGraph): networkx graph of model
        alt_node (str): node label | optional: move flows to this node

    Returns:
        SwmmInput: inp data
    """
    for section in NODE_SECTIONS + [sec.COORDINATES]:
        if (section in inp) and (node_label in inp[section]):
            inp[section].pop(node_label)

    if (sec.TAGS in inp) and ((Tag.TYPES.Node, node_label) in inp.TAGS):
        del inp[sec.TAGS][(Tag.TYPES.Node, node_label)]

    # AND delete connected links
    if graph is not None:
        if node_label in graph:
            links = next_links_labels(graph, node_label) + previous_links_labels(graph, node_label)  # type: List[str]
            graph.remove_node(node_label)
        else:
            links = list()
    else:
        links = list()
        for section in LINK_SECTIONS:
            if section in inp:
                links += list(inp[section].filter_keys([node_label], by='FromNode')) + \
                         list(inp[section].filter_keys([node_label], by='ToNode'))  # type: List[Conduit]
        links = [l.Name for l in links]  # type: List[str]

    for link in links:
        delete_link(inp, link)

    if alt_node is not None:
        move_flows(inp, node_label, alt_node)

    return inp


def move_flows(inp: SwmmInput, from_node, to_node, only_constituent=None):
    """
    move flow (INFLOWS or DWF) from one node to another

    Args:
        inp (SwmmInput): inp data
        from_node (str): first node label
        to_node (str): second node label
        only_constituent (list): only consider this constituent (default: FLOW)

    Notes:
        works inplace
    """
    for section in (sec.INFLOWS, sec.DWF):
        if section not in inp:
            continue

        if only_constituent is None:
            only_constituent = [DryWeatherFlow.TYPES.FLOW]

        for constituent in only_constituent:
            index_old = (from_node, constituent)

            if index_old in inp[section]:
                index_new = (to_node, constituent)

                obj = inp[section].pop(index_old)
                obj.Node = to_node

                if index_new not in inp[section]:
                    inp[section].add_obj(obj)

                elif section == sec.DWF:
                    # DryWeatherFlow can be easily added when Patterns are equal
                    inp[section][index_new].Base += obj.Base

                    # if not all([old[p] == new[p] for p in ['pattern1', 'pattern2', 'pattern3', 'pattern4']]):
                    #     print(f'WARNING: move_flows  from "{from_node}" to "{to_node}". DWF patterns don\'t
                    #     match!')

                elif section == sec.INFLOWS:
                    # Inflows can't be added due to the multiplication factor / timeseries
                    # if (TimeSeries, Type, Mfactor, Sfactor,Pattern) are equal then sum(Baseline)
                    print(f'WARNING: move_flows  from "{from_node}" to "{to_node}". Already Exists!')

            # else:
            #     print(f'Nothing to move from "{from_node}" [{section}]')


def delete_link(inp: SwmmInput, link):
    for s in LINK_SECTIONS + [sec.XSECTIONS, sec.LOSSES, sec.VERTICES]:
        if (s in inp) and (link in inp[s]):
            inp[s].pop(link)

    if (sec.TAGS in inp) and ((Tag.TYPES.Link, link) in inp.TAGS):
        del inp[sec.TAGS][(Tag.TYPES.Link, link)]


def delete_subcatchment(inp: SwmmInput, subcatchment):
    for s in [sec.SUBCATCHMENTS, sec.SUBAREAS, sec.INFILTRATION, sec.POLYGONS, sec.LOADINGS, sec.COVERAGES]:
        if (s in inp) and (subcatchment in inp[s]):
            inp[s].pop(subcatchment)

    if (sec.TAGS in inp) and ((Tag.TYPES.Subcatch, subcatchment) in inp.TAGS):
        del inp[sec.TAGS][(Tag.TYPES.Subcatch, subcatchment)]


def split_conduit(inp, conduit, intervals=None, length=None, from_inlet=True):
    # mode = [cut_point (GUI), intervals (n), length (l)]
    nodes = nodes_dict(inp)
    if isinstance(conduit, str):
        conduit = inp[sec.CONDUITS][conduit]  # type: Conduit

    dx = 0
    n_new_nodes = 0
    if intervals:
        dx = conduit.Length / intervals
        n_new_nodes = intervals - 1
    elif length:
        dx = length
        n_new_nodes = ceil(conduit.Length / length - 1)

    from_node = nodes[conduit.FromNode]
    to_node = nodes[conduit.ToNode]

    from_node_coord = inp[sec.COORDINATES][from_node.Name]
    to_node_coord = inp[sec.COORDINATES][to_node.Name]

    loss = None
    if (sec.LOSSES in inp) and (conduit.Name in inp[sec.LOSSES]):
        loss = inp[sec.LOSSES][conduit.Name]  # type: Loss

    new_nodes = list()
    new_links = list()

    x = dx
    last_node = from_node
    for new_node_i in range(n_new_nodes + 1):
        if x >= conduit.Length:
            node = to_node
        else:
            node = Junction(Name=f'{from_node.Name}_{to_node.Name}_{chr(new_node_i + 97)}',
                            Elevation=interp(x, [0, conduit.Length], [from_node.Elevation, to_node.Elevation]),
                            MaxDepth=interp(x, [0, conduit.Length], [from_node.MaxDepth, to_node.MaxDepth]),
                            InitDepth=interp(x, [0, conduit.Length], [from_node.InitDepth, to_node.InitDepth]),
                            SurDepth=interp(x, [0, conduit.Length], [from_node.SurDepth, to_node.SurDepth]),
                            Aponded=float(mean([from_node.Aponded, to_node.Aponded])),
                            )
            new_nodes.append(node)
            inp[sec.JUNCTIONS].add_obj(node)

            # TODO: COORDINATES based on vertices
            inp[sec.COORDINATES].add_obj(Coordinate(node.Name,
                                                    x=interp(x, [0, conduit.Length],
                                                                [from_node_coord.x, to_node_coord.x]),
                                                    y=interp(x, [0, conduit.Length],
                                                                [from_node_coord.y, to_node_coord.y])))

        link = Conduit(Name=f'{conduit.Name}_{chr(new_node_i + 97)}',
                       FromNode=last_node.Name,
                       ToNode=node.Name,
                       Length=dx,
                       Roughness=conduit.Roughness,
                       InOffset=0 if new_node_i != 0 else conduit.InOffset,
                       OutOffset=0 if new_node_i != (n_new_nodes - 1) else conduit.OutOffset,
                       InitFlow=conduit.InitFlow,
                       MaxFlow=conduit.MaxFlow)
        new_links.append(link)
        inp[sec.CONDUITS].add_obj(link)

        xs = inp[sec.XSECTIONS][conduit.Name].copy()
        xs.Link = link.Name
        inp[sec.XSECTIONS].add_obj(xs)

        if loss:
            inlet = loss.Inlet if loss.Inlet and (new_node_i == 0) else 0
            outlet = loss.Outlet if loss.Outlet and (new_node_i == n_new_nodes - 1) else 0
            average = loss.Average / (n_new_nodes + 1)
            flap_gate = loss.FlapGate

            if any([inlet, outlet, average, flap_gate]):
                inp[sec.LOSSES].add_obj(Loss(link.Name, inlet, outlet, average, flap_gate))

        # TODO: VERTICES

        if node is to_node:
            break
        last_node = node
        x += dx

    # if conduit.Name in inp[sec.VERTICES]:
    #     pass
    # else:
    #     # interpolate coordinates
    #     pass

    delete_link(inp, conduit.Name)


def combine_vertices(inp: SwmmInput, label1, label2):
    if sec.COORDINATES not in inp:
        # if there are not coordinates this function is nonsense
        return

    vertices_class = Vertices

    if sec.VERTICES not in inp:
        # we will at least ad the coordinates of the common node
        inp[sec.VERTICES] = Vertices.create_section()
    else:
        vertices_class = inp[sec.VERTICES]._section_object

    new_vertices = list()

    if label1 in inp[sec.VERTICES]:
        new_vertices += list(inp[sec.VERTICES][label1].vertices)

    common_node = links_dict(inp)[label1].ToNode
    if common_node in inp[sec.COORDINATES]:
        new_vertices += [inp[sec.COORDINATES][common_node].point]

    if label2 in inp[sec.VERTICES]:
        new_vertices += list(inp[sec.VERTICES][label2].vertices)

    if label1 in inp[sec.VERTICES]:
        inp[sec.VERTICES][label1].vertices = new_vertices
    else:
        inp[sec.VERTICES].add_obj(vertices_class(label1, vertices=new_vertices))


def combine_conduits(inp, c1, c2, graph: DiGraph = None):
    """
    combine the two conduits to one keep attributes of the first (c1)

    works inplace

    Args:
        inp (SwmmInput): inp data
        c1 (str | Conduit): conduit 1 to combine
        c2 (str | Conduit): conduit 2 to combine
        graph (networkx.DiGraph): optional, runs faster with graph (inp representation)

    Returns:
        SwmmInput: inp data
    """
    if isinstance(c1, str):
        c1 = inp[sec.CONDUITS][c1]
    if isinstance(c2, str):
        c2 = inp[sec.CONDUITS][c2]
    # -------------------------
    if graph:
        graph.remove_edge(c1.FromNode, c1.ToNode)
    # -------------------------
    if c1.FromNode == c2.ToNode:
        c_first = c2.copy()  # type: Conduit
        c_second = c1.copy()  # type: Conduit
    elif c1.ToNode == c2.FromNode:
        c_first = c1.copy()  # type: Conduit
        c_second = c2.copy()  # type: Conduit
    else:
        raise EnvironmentError('Links not connected')

    # -------------------------
    # vertices + Coord of middle node
    combine_vertices(inp, c_first.Name, c_second.Name)

    # -------------------------
    c_new = c1  # type: Conduit
    # -------------------------
    common_node = c_first.ToNode
    c_new.FromNode = c_first.FromNode
    c_new.ToNode = c_second.ToNode
    # -------------------------
    if graph:
        graph.add_edge(c_new.FromNode, c_new.ToNode, label=c_new.Name)

    if isinstance(c_new, Conduit):
        c_new.Length = round(c1.Length + c2.Length, 1)

        # offsets
        c_new.InOffset = c_first.InOffset
        c_new.OutOffset = c_second.OutOffset

    # Loss
    if (sec.LOSSES in inp) and (c_new.Name in inp[sec.LOSSES]):
        print(f'combine_conduits {c1.Name} and {c2.Name}. BUT WHAT TO DO WITH LOSSES?')
        # add losses
        pass

    delete_node(inp, common_node, graph=graph, alt_node=c_new.FromNode)
    return c_new


def combine_conduits_keep_slope(inp, c1, c2, graph: DiGraph = None):
    nodes = nodes_dict(inp)
    new_out_offset = (- calc_slope(inp, c1) * c2.Length
                      + c1.OutOffset
                      + nodes[c1.ToNode].Elevation
                      - nodes[c2.ToNode].Elevation)
    c1 = combine_conduits(inp, c1, c2, graph=graph)
    c1.OutOffset = round(new_out_offset, 2)
    return c1


def dissolve_conduit(inp, c: Conduit, graph: DiGraph = None):
    """
    combine the two conduits to one

    Args:
        inp (SwmmInput): inp data
        c1 (str | Conduit): conduit 1 to combine
        c2 (str | Conduit): conduit 2 to combine
        keep_first (bool): keep first (of conduit 1) cross-section; else use second (of conduit 2)

    Returns:
        SwmmInput: inp data
    """
    common_node = c.FromNode
    for c_old in list(previous_links(inp, common_node, g=graph)):
        if graph:
            graph.remove_edge(c_old.FromNode, c_old.ToNode)

        c_new = c_old  # type: Conduit

        # vertices + Coord of middle node
        combine_vertices(inp, c_new.Name, c.Name)

        c_new.ToNode = c.ToNode
        # -------------------------
        if graph:
            graph.add_edge(c_new.FromNode, c_new.ToNode, label=c_new.Name)

        # Loss
        if sec.LOSSES in inp and c_new.Name in inp[sec.LOSSES]:
            print(f'dissolve_conduit {c.Name} in {c_new.Name}. BUT WHAT TO DO WITH LOSSES?')

        if isinstance(c_new, Conduit):
            c_new.Length = round(c.Length + c_new.Length, 1)
            # offsets
            c_new.OutOffset = c.OutOffset

    delete_node(inp, common_node, graph=graph, alt_node=c.ToNode)


def rename_node(inp: SwmmInput, old_label: str, new_label: str, g=None):
    """
    change node label

    Notes:
        works inplace
        CONTROLS Not Implemented!

    Args:
        inp (SwmmInput): inp data
        old_label (str): previous node label
        new_label (str): new node label
        g (
    """
    # ToDo: Not Implemented: CONTROLS

    # Nodes and basic node components
    for section in NODE_SECTIONS + [sec.COORDINATES, sec.RDII]:
        if (section in inp) and (old_label in inp[section]):
            inp[section][new_label] = inp[section].pop(old_label)
            if hasattr(inp[section][new_label], 'Name'):
                inp[section][new_label].Name = new_label
            else:
                inp[section][new_label].Node = new_label

    # tags
    if (sec.TAGS in inp) and ((Tag.TYPES.Node, old_label) in inp.TAGS):
        tag = inp[sec.TAGS].pop((Tag.TYPES.Node, old_label))
        tag.Name = new_label
        inp.TAGS.add_obj(tag)

    # subcatchment outlets
    if sec.SUBCATCHMENTS in inp:
        for obj in subcachtment_nodes_dict(inp)[old_label]:
            obj.Outlet = new_label
        # -------
        # for obj in inp.SUBCATCHMENTS.filter_keys([old_label], 'Outlet'):  # type: SubCatchment
        #     obj.Outlet = new_label
        # -------

    # link: from-node and to-node
    previous_links, next_links = links_connected(inp, old_label, g=g)
    for link in previous_links:
        link.ToNode = new_label

    for link in next_links:
        link.ToNode = new_label

    # -------
    # for section in [sec.CONDUITS, sec.PUMPS, sec.ORIFICES, sec.WEIRS, sec.OUTLETS]:
    #     if section in inp:
    #         for obj in inp[section].filter_keys([old_label], 'FromNode'):  # type: _Link
    #             obj.FromNode = new_label
    #
    #         for obj in inp[section].filter_keys([old_label], 'ToNode'):  # type: _Link
    #             obj.ToNode = new_label
    # -------

    # (dwf-)inflows
    constituents = [DryWeatherFlow.TYPES.FLOW]
    if sec.POLLUTANTS in inp:
        constituents += list(inp.POLLUTANTS.keys())

    for section in [sec.INFLOWS, sec.DWF, sec.TREATMENT]:
        if section in inp:
            for constituent in constituents:
                old_id = (old_label, constituent)
                if old_id in inp[section]:
                    inp[section][old_id].Node = new_label
                    inp[section][(new_label, constituent)] = inp[section].pop(old_id)

            # -------
            # for obj in inp[section].filter_keys([old_label], 'Node'):  # type: Inflow
            #     obj.Node = new_label
            #     inp[section][(new_label, obj[obj._identifier[1]])] = inp[section].pop((old_label,
            #     obj[obj._identifier[1]]))
            # -------


def rename_link(inp: SwmmInput, old_label: str, new_label: str):
    """
    change link label

    Notes:
        works inplace
        CONTROLS Not Implemented!

    Args:
        inp (SwmmInput): inp data
        old_label (str): previous link label
        new_label (str): new link label
    """
    # ToDo: Not Implemented: CONTROLS
    for section in LINK_SECTIONS + [sec.XSECTIONS, sec.LOSSES, sec.VERTICES]:
        if (section in inp) and (old_label in inp[section]):
            inp[section][new_label] = inp[section].pop(old_label)
            if hasattr(inp[section][new_label], 'Name'):
                inp[section][new_label].Name = new_label
            else:
                inp[section][new_label].Link = new_label

    if (sec.TAGS in inp) and ((Tag.TYPES.Link, old_label) in inp.TAGS):
        inp[sec.TAGS][(Tag.TYPES.Link, new_label)] = inp[sec.TAGS].pop((Tag.TYPES.Link, old_label))


def rename_timeseries(inp, old_label, new_label):
    """
    change timeseries label

    Notes:
        works inplace

    Args:
        inp (SwmmInput): inp data
        old_label (str): previous timeseries label
        new_label (str): new timeseries label
    """
    if old_label in inp[sec.TIMESERIES]:
        obj = inp[sec.TIMESERIES].pop(old_label)
        obj.Name = new_label
        inp[sec.TIMESERIES].add_obj(obj)

    key = EvaporationSection.KEYS.TIMESERIES  # TemperatureSection.KEYS.TIMESERIES, ...

    if sec.RAINGAGES in inp:
        f = inp[sec.RAINGAGES].frame
        filtered_table = f[(f['Source'] == key) & (f['Timeseries'] == old_label)]
        if not filtered_table.empty:
            for i in filtered_table.index:
                inp[sec.RAINGAGES][i].Timeseries = new_label

    if sec.EVAPORATION in inp:
        if key in inp[sec.EVAPORATION]:
            if inp[sec.EVAPORATION][key] == old_label:
                inp[sec.EVAPORATION][key] = new_label

    if sec.TEMPERATURE in inp:
        if key in inp[sec.TEMPERATURE]:
            if inp[sec.TEMPERATURE][key] == old_label:
                inp[sec.TEMPERATURE][key] = new_label

    if sec.OUTFALLS in inp:
        f = inp[sec.OUTFALLS].frame
        filtered_table = f[(f['Type'] == key) & (f['Data'] == old_label)]
        if not filtered_table.empty:
            for i in filtered_table.index:
                inp[sec.OUTFALLS][i].Data = new_label

    if sec.INFLOWS in inp:
        f = inp[sec.INFLOWS].frame
        filtered_table = f[f['TimeSeries'] == old_label]
        if not filtered_table.empty:
            for i in filtered_table.index:
                inp[sec.INFLOWS][i].TimeSeries = new_label
