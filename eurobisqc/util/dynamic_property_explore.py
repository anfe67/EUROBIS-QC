test_string_1 = '{"tragusLengthInMeters":0.014, "weightInGrams":120}'
test_string_2 = '"Net type: Bogorov-Rass; Net mouth opening: 0.8 m; Mesh size: 300 mkm"'
test_string_3 = "ObservedWeightInGrams=0.00052"
test_string_4 = '"Net type: Bogorov-Rass_Net mouth opening: 0.8 m_Mesh size: 300 mkm"'  # Failure not detected

strings = [test_string_1, test_string_2, test_string_3, test_string_4]
dicts = []

for s in strings:
    s = s.strip()
    if '{' in s:
        s = s.replace('{', '')
    if '}' in s:
        s = s.replace('}', '')
    if '"' in s:
        s = s.replace('"', '')
    if '=' in s:
        s = s.replace('=', ':')
    if ';' in s:
        s = s.replace(';', ':')
    if ',' in s:
        s = s.replace(',', ':')
    if '_' in s:
        s = s.replace('_', ':')

    s_l = s.split(':')
    if len(s_l) % 2 == 0:
        res_dct = {s_l[i]: s_l[i + 1] for i in range(0, len(s_l), 2)}
    else:
        res_dct = {'conversion_fail': True}
    dicts.append(res_dct)

for d in dicts:
    print(d)
