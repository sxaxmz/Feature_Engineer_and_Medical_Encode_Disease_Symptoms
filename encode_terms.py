import pandas as pd
import numpy as np
import json
from urllib.request import urlopen, Request
from urllib.parse import quote


file_name = 'Diseaes list with symp'
name_sheet = 'Sheet1'

baseUrl = 'https://browser.ihtsdotools.org/snowstorm/snomed-ct'
edition = 'MAIN'
version = '2019-07-31'

def urlopen_with_header(url):
    req = Request(url)
    req.add_header('User-Agent','Python')
    return urlopen(req)

def getSnomedCode(searchTerm):
    url = baseUrl + '/browser/' + edition + '/' + version + '/descriptions?term=' + quote(searchTerm) + '&conceptActive=true&groupByConcept=false&searchMode=STANDARD&offset=0&limit=50'
    response = urlopen_with_header(url).read()
    data = json.loads(response.decode('utf-8'))
    snomed_code = 0
    print('===== {} ====='.format(searchTerm))
    for term in data['items']:
      if searchTerm == term['term']:
        print("{} : {}".format(term['term'], term['concept']['conceptId']))
        snomed_code = term['concept']['conceptId']
    return snomed_code

df_symp = pd.read_excel('{}.xlsx'.format(file_name), sheet_name=name_sheet)
df = df_symp.drop('Disease Name', axis=1)

dict_symp, count, unique_symptoms = {}, 0, []
for col in list(df.columns):
  dict_symp[col] = set(df[col])
  print('Column Name: {} | Unique Symptoms {} out of '.format(col, len(set(df[col])), len(df[col])))
  count += len(set(df[col]))
for k, v in dict_symp.items():
  for symp in v:
    unique_symptoms.append(symp)
unique_symptoms = set(unique_symptoms)
unique_symptoms.discard(np.nan)
print('\n {} Unique Symptoms From Total {} Recorded Symptoms'.format(len(unique_symptoms), count))
print('List of Symptoms: \n {}'.format(unique_symptoms))


unique_symptoms_col = ['Disease Name']
selected_disease = list(df_symp['Disease Name'])
for s in list(unique_symptoms):
  unique_symptoms_col.append(s.strip())
output_df = pd.DataFrame(columns=unique_symptoms_col)
print('Column Names: ',unique_symptoms_col)

for disease in selected_disease:
  new_row = [disease, *[0]*len(list(output_df.columns)[1:])]
  for i, symp in enumerate(list(output_df.columns)[1:]):
    df = pd.read_excel('{}.xlsx'.format(file_name), sheet_name=name_sheet)
    tmp_disease_df = df[df['Disease Name'] == disease]
    if symp.strip() in list(tmp_disease_df.values[0][1:]):
       val = 1
    else:
       val = 0
    new_row[list(output_df.columns).index(symp)] = val
  print('Row ({})-> '.format(len(output_df.index)), len(new_row), new_row)
  output_df.loc[len(output_df.index)] = new_row
output_df.head(len(output_df))
output_df.to_excel('Feature_Engineered_{}.xlsx'.format(file_name))

encoded_symp = []
rename_dict = {'Disease Name': 'Disease Name'}
for symp in list(output_df.columns)[1:]:
  rename_dict[symp] = getSnomedCode(symp)
output_df.rename(rename_dict, axis=1, inplace=True)

encoded_disease = []
for disease_name in list(output_df['Disease Name']):
  encoded_disease.append(getSnomedCode(disease_name))
output_df['Disease Name'] = encoded_disease
output_df.to_excel('Snomed_Encoded_{}.xlsx'.format(file_name))