def calculate_cost(num_pages, color):
    cost_per_page = 2

    if color == "color":
        cost_per_page = 10

    return num_pages * cost_per_page
