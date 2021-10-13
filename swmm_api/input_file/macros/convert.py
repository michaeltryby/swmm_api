from .. import section_labels as sec
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
    j = inp[sec.JUNCTIONS].pop(label)  # type: Junction
    if sec.STORAGE not in inp:
        inp[sec.STORAGE] = Storage.create_section()
    inp[sec.STORAGE].add_obj(Storage(Name=label, Elevation=j.Elevation, MaxDepth=j.MaxDepth,
                                     InitDepth=j.InitDepth, Apond=j.Aponded, *args, **kwargs))


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
    j = inp[sec.JUNCTIONS].pop(label)  # type: Junction
    if sec.OUTFALLS not in inp:
        inp[sec.OUTFALLS] = Outfall.create_section()
    inp[sec.OUTFALLS].add_obj(Outfall(Name=label, Elevation=j.Elevation, *args, **kwargs))


def conduit_to_orifice(inp, label, Type, Offset, Qcoeff, FlapGate=False, Orate=0):
    """
    convert :class:`~swmm_api.input_file.inp_sections.link.Conduit` to
    :class:`~swmm_api.input_file.inp_sections.link.Orifice`

    and add it to the ORIFICES section

    Args:
        inp (SwmmInput): inp-file data
        label (str): label of the conduit
        Type (str): orientation of orifice: either SIDE or BOTTOM.
        Offset (float): amount that a Side Orifice’s bottom or the position of a Bottom Orifice is offset above
            the invert of inlet node (ft or m, expressed as either a depth or as an elevation,
            depending on the LINK_OFFSETS option setting).
        Qcoeff (float): discharge coefficient (unitless).
        FlapGate (bool): YES if flap gate present to prevent reverse flow, NO if not (default is NO).
        Orate (int): time in decimal hours to open a fully closed orifice (or close a fully open one).
                        Use 0 if the orifice can open/close instantaneously.
    """
    c = inp[sec.CONDUITS].pop(label)  # type: Conduit
    if sec.ORIFICES not in inp:
        inp[sec.ORIFICES] = Orifice.create_section()
    inp[sec.ORIFICES].add_obj(Orifice(Name=label, FromNode=c.FromNode, ToNode=c.ToNode,
                                      Type=Type, Offset=Offset, Qcoeff=Qcoeff, FlapGate=FlapGate, Orate=Orate))
