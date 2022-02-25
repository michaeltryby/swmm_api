import shape_generator
from .macros import find_link
from ..sections import CrossSection, Pump
from ..inp import SwmmInput


VIRTUAL_LENGTH = 100


def get_cross_section_maker(inp, link_label):
    """
    Get a cross-section object.

    Object type from the package `SWMM-xsections-shape-generator` to analyse and plot cross-sections.

    Args:
        inp (SwmmInput): inp-data
        link_label (str): label of the link, where the cross-section is wanted

    Returns:
        shape_generator.CrossSection: cross-section object of the selected link
    """
    c = find_link(inp, link_label)
    if c is None:
        return  # not found
    if isinstance(c, Pump):
        return
    xs = inp.XSECTIONS[link_label]

    if xs.Shape == CrossSection.SHAPES.CUSTOM:
        curve = inp.CURVES[xs.Curve]
        return shape_generator.CrossSection.from_curve(curve, height=VIRTUAL_LENGTH)
    elif xs.Shape == CrossSection.SHAPES.IRREGULAR:
        return  # Todo: I don't know how
    elif xs.Shape in [CrossSection.SHAPES.RECT_OPEN, CrossSection.SHAPES.RECT_CLOSED]:
        return  # Todo: Rect
    else:
        return shape_generator.swmm_std_cross_sections(xs.Shape, height=VIRTUAL_LENGTH)


def profil_area(inp, link_label):
    """
    Get the area of the link with a given cross-section.

    Args:
        inp (SwmmInput): inp-data
        link_label (str): label of the link, where the cross-section area is wanted

    Returns:
        float: area of the cross-section in m²
    """
    cs = get_cross_section_maker(inp, link_label)
    if cs is None:
        return
    xs = inp.XSECTIONS[link_label]

    if xs.Shape == CrossSection.SHAPES.CUSTOM:
        return cs.area_v / VIRTUAL_LENGTH ** 2 * xs.Geom1
    elif xs.Shape == CrossSection.SHAPES.IRREGULAR:
        return  # Todo: I don't know how
    elif xs.Shape in [CrossSection.SHAPES.RECT_OPEN, CrossSection.SHAPES.RECT_CLOSED]:
        return xs.Geom1 * xs.Geom2
    else:
        return cs.area_v / VIRTUAL_LENGTH ** 2 * xs.Geom1


def velocity(inp, link_label, flow):
    # TODO
    cs = get_cross_section_maker(inp, link_label)
    if cs is None:
        return
    xs = inp.XSECTIONS[link_label]
