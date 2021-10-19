from shape_generator.converter_swmm_api import from_swmm_shape
from shape_generator.swmm_std_cross_sections import swmm_std_cross_sections
from . import find_link
from ..sections import CrossSection, Pump
from ... import SwmmInput


VIRTUAL_LENGTH = 100


def get_cross_section_maker(inp: SwmmInput, link_label: str):
    c = find_link(inp, link_label)
    if c is None:
        return  # not found
    if isinstance(c, Pump):
        return
    xs = inp.XSECTIONS[link_label]

    if xs.Shape == CrossSection.SHAPES.CUSTOM:
        curve = inp.CURVES[xs.Curve]
        return from_swmm_shape(curve, height=VIRTUAL_LENGTH)
    elif xs.Shape == CrossSection.SHAPES.IRREGULAR:
        return  # Todo: I don't know how
    elif xs.Shape in [CrossSection.SHAPES.RECT_OPEN, CrossSection.SHAPES.RECT_CLOSED]:
        return  # Todo: Rect
    else:
        return swmm_std_cross_sections(xs.Shape, height=VIRTUAL_LENGTH)


def profil_area(inp: SwmmInput, link_label: str):
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


def velocity(inp: SwmmInput, link_label, flow):
    cs = get_cross_section_maker(inp, link_label)
    if cs is None:
        return
    xs = inp.XSECTIONS[link_label]
