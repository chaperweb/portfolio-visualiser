from portfolio_manager.models import Project


def oob_assign(array,index,item,default):
  # set array[index] to item. if index is out of bounds,
  # array is extended as necessary using default
  array.extend([default]*(index-len(array)+1))
  array[index]=(item)


def get_data_array():
    field_names = ['ID', 'Updated', 'MilestoneDueDate']
    field_types = ['', '', '']
    data_dict = {}
    data = []
    all_projects = Project.objects.all()

    for project in all_projects:
        dims = project.dimensions.all()
        for dim in dims:
            dim_obj = dim.dimension_object
            name = dim_obj.name
            if name not in field_names:
                field_names.append(name)
                field_types.append(dim_obj.data_type)
            if hasattr(dim_obj, 'history'):
                histories = dim_obj.history.all()
                for his in histories:
                    key = (project.id, his.history_date)
                    try:
                        data_dict[key].append((his.name, his.export_string()))
                    except KeyError:
                        data_dict[key] = [(his.name, his.export_string())]

    for pid_date, values in data_dict.items():
        data_row = ['']*len(field_names)
        data_row[0] = pid_date[0]
        data_row[1] = pid_date[1].strftime('%d/%m/%Y')
        for v in values:
            index = field_names.index(v[0])
            oob_assign(data_row, index, v[1], '')
        data.append(data_row)

    final_data = [field_names]
    final_data.append(field_types)
    final_data.extend(data)

    print("--- DATA ---")
    print(data)
    # print("---NAMES---")
    # print(field_names)
    # print("---TYPES---")
    # print(field_types)
    # print("---DATA---")
    # print(data_dict)
    return final_data
