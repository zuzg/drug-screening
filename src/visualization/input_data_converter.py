#if data has form of series and label use this
def convert_inpute_data(series, label): 
  data = {}
  unique_label = (list(set(label)))
  for i in unique_label:
    data[i] = []
  for i in range(len(series)):
    data[label[i]].append(series[i])
  list_of_lists = []
  for i in unique_label:
    list_of_lists.append(data[i])
  return list_of_lists