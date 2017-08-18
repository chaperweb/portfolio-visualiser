from portfolio_manager.models import Project

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
                        data_dict[key].append((his.name, his.string()))
                    except KeyError:
                        data_dict[key] = [(his.name, his.string())]

    for date_pid, values in data_dict.items():
        data_row = [date_pid[1], date_pid[0], '']
        print(date_pid)
        for v in values:
            print(v[0] + ": " + v[1])
            index = field_names.index(v[0])
            print("i: " + index)
            data_row[index] = v[1]
            #https://stackoverflow.com/questions/20694420/out-of-bounds-assignment-to-a-python-array-am-i-reinventing-a-wheel

    print("--- DATA ---")
    print(data)
    # print("---NAMES---")
    # print(field_names)
    # print("---TYPES---")
    # print(field_types)
    # print("---DATA---")
    # print(data)
