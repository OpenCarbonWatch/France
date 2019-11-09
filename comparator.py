import pandas as pd

organizations = pd.read_csv('../data/output/organizations.csv', dtype=str)
assessments = pd.read_csv('../data/BEGES/assessments.csv', dtype=str)
legal_units = pd.read_csv('../data/BEGES/legal_units.csv', dtype=str)

# Add (some) missing links between organization codes and assessments

links = pd.read_csv('links.csv', dtype=str)
legal_units = legal_units.append(links, ignore_index=True)

# Filter partial assessments

assessments = assessments[pd.to_numeric(assessments['total_scope_1']) + pd.to_numeric(assessments['total_scope_2']) > 0]

# Bind with assessments

organizations['last_assessment'] = ''
organizations['with_action_plan'] = ''
organizations['with_scope_3'] = ''
organizations['links'] = ''

for i in range(organizations.shape[0]):
    code = organizations.at[i, 'id']
    ass_ids = legal_units[legal_units['siren_code'] == code]['assessment_id'].tolist()
    org_ass = assessments[assessments['id'].isin(ass_ids)]
    if org_ass.shape[0] > 0:
        year = max([int(y) for y in org_ass['reporting_year'].tolist()])
        org_ass = org_ass[org_ass['reporting_year'] == str(year)]
        organizations.at[i, 'last_assessment'] = year
        organizations.at[i, 'with_action_plan'] = 'Oui' in ''.join(org_ass['action_plan'].tolist())
        organizations.at[i, 'with_scope_3'] = pd.to_numeric(org_ass['total_scope_3']).sum() > 0
        organizations.at[i, 'links'] = "\n".join(org_ass['source_url'].tolist())

organizations.to_csv('../data/output/OCW_France.csv', index=False, encoding='UTF-8')
with pd.ExcelWriter('../data/output/OCW_France.xlsx', engine='xlsxwriter', options={'strings_to_urls': False}) as writer:
    organizations.to_excel(writer, sheet_name='Organizations', index=False)
