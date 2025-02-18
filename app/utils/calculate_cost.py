def calculate_cost(num_pages, print_type, color):
    cost_per_page = 2

    if color == "color":
        cost_per_page = 10

    # if print_type == "double-sided":
    #     cost_per_page *= 0.75

    return num_pages * cost_per_page
