

from swmm_api.report_file.report import Report

r = Report('report_file_1.rpt')

#
# l = list()
# for i in r.raw_parts.keys():
#     l.append('_'.join(i.lower().split()))
#
# for i in l:
#     print(f'self.{i}')

r.node_flooding_summary
print()

