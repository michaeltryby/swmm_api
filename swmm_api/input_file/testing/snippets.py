import yaml
from pandas import DataFrame, Series

from ..helpers.type_converter import type2str


def network2yaml(inp, fn):
    """

    Args:
        inp (swmm_api.input_file.inp_helpers.InpData):
    """
    basic_nw = inp.copy()
    for head, data in basic_nw.items():
        if isinstance(data, DataFrame):
            basic_nw[head] = data.applymap(type2str).to_dict(orient='index')
        elif isinstance(data, Series):
            basic_nw[head] = data.apply(type2str).to_dict()

    yaml.dump(basic_nw, open(fn + '.yaml', 'w'), default_flow_style=False)
