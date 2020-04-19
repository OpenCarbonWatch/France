import pandas as pd
import sys

# Base file path for data

output_path = sys.argv[1]
old_path = output_path + sys.argv[2] + '/assessments.csv'
new_path = output_path + sys.argv[3] + '/assessments.csv'

# Compare old and new assessments

old_assessments = pd.read_csv(old_path, index_col=False, encoding='UTF-8')
new_assessments = pd.read_csv(new_path, index_col=False, encoding='UTF-8')

old_assessments = old_assessments[old_assessments['is_draft'] == 'Non']
new_assessments = new_assessments[new_assessments['is_draft'] == 'Non']

new_assessments = new_assessments[~ new_assessments['id'].isin(old_assessments['id'])]

print("Total number of new published assessments: %d." % new_assessments.shape[0])

# Look for high quality new assessments

good = new_assessments
good['total'] = good['total_scope_1'] + good['total_scope_2'] + good['total_scope_3']
good['reductions'] = good.fillna(0)['reductions_scope_1_2'] + good.fillna(0)['reductions_scope_1'] + good.fillna(0)['reductions_scope_2'] + good.fillna(0)['reductions_scope_3']
good['ratio'] = good['reductions'] / good['total']
good['is_good'] = True
good.loc[good['total_scope_3'] <= 0, 'is_good'] = False
good.loc[good['ratio'] < 0.05, 'is_good'] = False
good.loc[good['ratio'] > 0.33, 'is_good'] = False

good.to_excel(output_path + 'new.xlsx', index=False)
