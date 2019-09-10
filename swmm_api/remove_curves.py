from swmm_api.input_file.inp_macros import InpMacros
from os import path


if __name__ == '__main__':
    fn = path.join('D:', 'Downloads', '20181120_Graz_Annabach.inp')
    nw = InpMacros.from_file(filename=path.join('model', fn), drop_gui_part=False)
    nw.reduce_curves()
    nw.write(fn.replace('.inp', '_reduced.inp'))
