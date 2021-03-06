from ..section_labels import JUNCTIONS, CONDUITS, STORAGE, OUTFALLS, ORIFICES
from ..sections import Storage, Outfall, Orifice


def junction_to_storage(inp, label, *args, **kwargs):
    """
    convert :class:`~swmm_api.input_file.inp_sections.node.Junction` to
    :class:`~swmm_api.input_file.inp_sections.node.Storage`

    and add it to the STORAGE section

    Args:
        inp (SwmmInput): inp-file data
        label (str): label of the junction
        *args: argument of the :class:`~swmm_api.input_file.inp_sections.node.Storage`-class
        **kwargs: keyword arguments of the :class:`~swmm_api.input_file.inp_sections.node.Storage`-class
    """
    j = inp[JUNCTIONS].pop(label)  # type: Junction
    if STORAGE not in inp:
        inp[STORAGE] = Storage.create_section()
    inp[STORAGE].add_obj(Storage(name=label, elevation=j.elevation, depth_max=j.depth_max,
                                 depth_init=j.depth_init, depth_surcharge=j.area_ponded, *args, **kwargs))


def junction_to_outfall(inp, label, *args, **kwargs):
    """
    convert :class:`~swmm_api.input_file.inp_sections.node.Junction` to
    :class:`~swmm_api.input_file.inp_sections.node.Outfall`

    and add it to the OUTFALLS section

    Args:
        inp (SwmmInput): inp-file data
        label (str): label of the junction
        *args: argument of the :class:`~swmm_api.input_file.inp_sections.node.Outfall`-class
        **kwargs: keyword arguments of the :class:`~swmm_api.input_file.inp_sections.node.Outfall`-class
    """
    j = inp[JUNCTIONS].pop(label)  # type: Junction
    if OUTFALLS not in inp:
        inp[OUTFALLS] = Outfall.create_section()
    inp[OUTFALLS].add_obj(Outfall(name=label, elevation=j.elevation, *args, **kwargs))


def conduit_to_orifice(inp, label, Type, Offset, Qcoeff, has_flap_gate=False, Orate=0):
    """
    convert :class:`~swmm_api.input_file.inp_sections.link.Conduit` to
    :class:`~swmm_api.input_file.inp_sections.link.Orifice`

    and add it to the ORIFICES section

    Args:
        inp (SwmmInput): inp-file data
        label (str): label of the conduit
        Type (str): orientation of orifice: either SIDE or BOTTOM.
        Offset (float): amount that a Side Orifice???s bottom or the position of a Bottom Orifice is offset above
            the invert of inlet node (ft or m, expressed as either a depth or as an elevation,
            depending on the LINK_OFFSETS option setting).
        Qcoeff (float): discharge coefficient (unitless).
        has_flap_gate (bool): YES if flap gate present to prevent reverse flow, NO if not (default is NO).
        Orate (int): time in decimal hours to open a fully closed orifice (or close a fully open one).
                        Use 0 if the orifice can open/close instantaneously.
    """
    c = inp[CONDUITS].pop(label)  # type: Conduit
    if ORIFICES not in inp:
        inp[ORIFICES] = Orifice.create_section()
    inp[ORIFICES].add_obj(Orifice(name=label, from_node=c.from_node, to_node=c.to_node,
                                  orientation=Type, offset=Offset, discharge_coefficient=Qcoeff, has_flap_gate=has_flap_gate, hours_to_open=Orate))
