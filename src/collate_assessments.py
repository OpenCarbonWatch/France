import pandas as pd

data_path = '../data/'
input_path = '../input/'
output_path = '../output/'

# Add (some) missing links between organization codes and assessments

links_ademe = pd.read_csv(input_path + 'BEGES/legal_units.csv', dtype=str)
links_ademe = links_ademe[links_ademe['legal_unit_id_type'] == 'SIREN']
del links_ademe['legal_unit_id_type']
links_ademe = links_ademe.rename(columns={'legal_unit_id': 'organization_id'})

# Some assessments refer to the wrong SIRET in ADEME's online data. We override them by our manual file.
links_ademe = links_ademe[links_ademe['assessment_id'] != '4787']
links_ademe = links_ademe[links_ademe['assessment_id'] != '9141']
links_ademe = links_ademe[links_ademe['assessment_id'] != '9551']

links_ademe = links_ademe[['organization_id', 'assessment_id']].copy()
links_manual = pd.read_csv(data_path + 'manual_assessment_organization.csv', dtype=str)
links = links_manual.append(links_ademe, ignore_index=True)
links.to_csv(output_path + 'assessment_organization.csv', index=False, encoding='UTF-8')

# Filter columns for assessments

assessments = pd.read_csv(input_path + 'BEGES/assessments.csv', dtype=str)
assessments = assessments[assessments['is_draft'] == 'Non']
assessments = assessments[['id', 'reporting_year', 'total_scope_1', 'total_scope_2', 'total_scope_3', 'action_plan',
                           'reductions_scope_1_2', 'reductions_scope_1', 'reductions_scope_2', 'reductions_scope_3',
                           'source_url']]
assessments['action_plan'] = (assessments['action_plan'] == 'Oui')
assessments.to_csv(output_path +  'assessments.csv', index=False, encoding='UTF-8')

# Reporting on missing matches

missing = assessments[~ assessments['id'].isin(links['assessment_id'])]
missing.to_csv(output_path + 'missing.csv', index=False, sep=';', encoding='UTF-8')
