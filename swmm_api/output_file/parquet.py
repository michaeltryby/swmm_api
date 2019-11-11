__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from pandas import read_parquet, MultiIndex, Series
import numpy as np

"""
extension to pandas parquet reader and writer

because MultiIndex and integers are not supported as index/columns


index.freq & index/column name are not implemented by parquet
2019-01-12
"""


def _check_name(filename):
    """
    check if name has a common parquet file-extension
    Args:
        filename (str): old filename with or without extension

    Returns:
        str: new filename with extension
    """
    if not (filename.endswith('.parq') or filename.endswith('.parquet')):
        filename += '.parq'
    return filename


def _multiindex_to_index(multiindex):
    """

    Args:
        multiindex (pandas.MultiIndex): old index with multiple level

    Returns:
        pandas.Index: new index with one levels
    """
    if isinstance(multiindex, MultiIndex):
        # compact_name = '/'.join(str(c) for c in multiindex.names)
        multiindex = ['/'.join(str(c) for c in col).strip() for col in multiindex.values]
        # multiindex.name = compact_name
    return multiindex


def write(data, filename, compression='brotli'):
    """
    write data to parquet

    Args:
        data (pandas.DataFrame):
        filename (str): path to resulting file
        compression (str):
    """
    filename = _check_name(filename)
    if isinstance(data, Series):
        df = data.to_frame()
    else:
        df = data.copy()

    df.index = _multiindex_to_index(df.index)
    df.columns = _multiindex_to_index(df.columns)

    df.to_parquet(filename, compression=compression)


def _index_to_multiindex(index):
    """

    Args:
        index (pandas.Index): old index with one level

    Returns:
        pandas.MultiIndex: new index with multiple levels
    """
    if (index.dtype == np.object) and index.str.contains('/').all():
        # old_name = index.name
        index = MultiIndex.from_tuples([col.split('/') for col in index])
        # if isinstance(old_name, str):
        #     new_names = old_name.split('/')
        #     index.names = new_names
    return index


def read(filename):
    """
    read parquet file

    Args:
        filename (str): path to parquet file

    Returns:
        pandas.DataFrame: data
    """
    filename = _check_name(filename)
    df = read_parquet(filename)
    df.columns = _index_to_multiindex(df.columns)
    df.index = _index_to_multiindex(df.index)
    return df
