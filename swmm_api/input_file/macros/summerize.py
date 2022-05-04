from swmm_api import SwmmInput
from swmm_api.input_file import SEC
from swmm_api.input_file.macros import nodes_dict, links_dict


def print_summary(inp):
    """
    Print basic summary of the inp-data.

    Args:
        inp (SwmmInput): inp-data
    """
    if SEC.OPTIONS in inp and "ROUTING_STEP" in inp.OPTIONS:
        print(f'ROUTING_STEP: {inp.OPTIONS["ROUTING_STEP"]}')
    print(f'NODES: {len(nodes_dict(inp)):_d}')
    print(f'LINKS: {len(links_dict(inp)):_d}')
    if SEC.SUBAREAS in inp:
        print(f'SUBCATCHMENTS: {len(inp.SUBAREAS.keys()):_d}')
    if SEC.POLLUTANTS in inp:
        print(f'POLLUTANTS: {len(inp.POLLUTANTS.keys()):_d}')
