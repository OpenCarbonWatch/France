import pandas as pd

# Add (some) missing links between organization codes and assessments

links_ademe = pd.read_csv('../data/BEGES/legal_units.csv', dtype=str)
links_ademe = links_ademe[links_ademe['legal_unit_id_type'] == 'SIREN']
del links_ademe['legal_unit_id_type']
links_ademe = links_ademe.rename(columns={'legal_unit_id': 'organization_id'})
links_ademe = links_ademe[['organization_id', 'assessment_id']].copy()
links_manual = pd.read_csv('manual_assessment_organization.csv', dtype=str)
links = links_manual.append(links_ademe, ignore_index=True)
links.to_csv('../data/output/assessment_organization.csv', index=False, encoding='UTF-8')

# Filter columns for assessments

assessments = pd.read_csv('../data/BEGES/assessments.csv', dtype=str)
assessments = assessments[['id', 'reporting_year', 'total_scope_1', 'total_scope_2', 'total_scope_3', 'action_plan',
                           'reductions_scope_1_2', 'reductions_scope_1', 'reductions_scope_2', 'reductions_scope_3',
                           'is_draft', 'source_url']]
assessments['action_plan'] = (assessments['action_plan'] == 'Oui')
assessments['is_draft'] = (assessments['is_draft'] == 'Oui')
assessments.to_csv('../data/output/assessments.csv', index=False, encoding='UTF-8')

# Reporting on missing matches

missing = assessments[~ assessments['id'].isin(links['assessment_id'])]
missing = missing[~ missing['is_draft']]
missing.to_csv('../data/output/missing.csv', index=False, sep=';', encoding='UTF-8')
