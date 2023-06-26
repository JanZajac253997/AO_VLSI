import random
import math
import time

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle as MatplotlibRectangle

class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.orientation = 0  # Default orientation is 0 (width > height)
        self.placed = False
        self.x = None
        self.y = None

def flip(rectangle):
    rectangle.width, rectangle.height = rectangle.height, rectangle.width
    rectangle.orientation = 1 if rectangle.orientation == 0 else 1

def is_overlap(rect1, rect2):
    if rect1.x < rect2.x + rect2.width and rect1.x + rect1.width > rect2.x:
        if rect1.y < rect2.y + rect2.height and rect1.y + rect1.height > rect2.y:
            return True
    return False

def move_rectangle(x, y, rectangle, rectangles):
    save_x = rectangle.x
    save_y = rectangle.y
    rectangle.x = x
    rectangle.y = y
    if any(is_overlap(rectangle, placed_rect) for placed_rect in rectangles if placed_rect.placed and placed_rect != rectangle):
        rectangle.x = save_x
        rectangle.y = save_y
        return False
    else:
        return True

def find_non_overlapping_arrangement(rectangles):
    rectangles.sort(key=lambda r: r.width * r.height, reverse=True)  # Sort by area in descending order
    ile = len(rectangles)
    area = sum(r.height+r.width for r in rectangles)
    side = int(math.sqrt(area)+1)
    height = side*int(math.sqrt(ile)+1)
    width = side*int(math.sqrt(ile)+1)
    #width = max(rectangles, key=lambda r: r.width).width
    #height = sum(r.height for r in rectangles)

    canvas = [[0] * width for _ in range(height)]

    for rect in rectangles:
        for y in range(height - rect.height + 1):
            for x in range(width - rect.width + 1):
                if move_rectangle(x, y, rect, rectangles):
                    rect.placed = True
                    for j in range(rect.height):
                        for i in range(rect.width):
                            canvas[y + j][x + i] = 1
                    break
            if rect.placed:
                break

    return canvas, width, height

def read_rectangles_from_file(file_path):
    rectangles = []
    with open(file_path, 'r') as file:
        for line in file:
            width, height = line.strip().split(',')
            rectangle = Rectangle(int(width), int(height))
            rectangles.append(rectangle)
    return rectangles

def save_results_to_file(rectangles):
    with open('results.txt', 'w') as file:
        for rect in rectangles:
            if rect.width < rect.height:  # Check orientation based on width and height
                flip(rect)
            file.write(f"{rect.x},{rect.y},{rect.orientation}\n")

def plot_rectangles(rectangles):
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')


    for rect in rectangles:

        bottom_left = (rect.x, rect.y)
        rectangle = MatplotlibRectangle(bottom_left, rect.width, rect.height, edgecolor='black', facecolor='none')
        ax.add_patch(rectangle)

        plt.text(rect.x + rect.width / 2, rect.y + rect.height / 2, f"({rect.x}, {rect.y})",
                 horizontalalignment='center', verticalalignment='center')
    ax.set_xlim(0, max(rect.x + rect.width for rect in rectangles))
    ax.set_ylim(0, max(rect.y + rect.height for rect in rectangles))
    plt.savefig('visualization.png')
    plt.show()

def calculate_smallest_rectangle_area(rectangles):
    for rect in rectangles:
        if rect.orientation == 1:
            rect.width, rect.height = rect.height, rect.width
    max_x = max(rect.x + rect.width for rect in rectangles)
    max_y = max(rect.y + rect.height for rect in rectangles)
    total_area = max_x * max_y

    filled_area = sum(rect.width * rect.height for rect in rectangles)
    empty_area = total_area - filled_area

    empty_percentage = (empty_area / total_area) * 100

    return max_x * max_y, (max_x, max_y), empty_percentage

def swap_rectangles(rect1, rect2):
    rect1.x, rect2.x = rect2.x, rect1.x
    rect1.y, rect2.y = rect2.y, rect1.y

def simulated_annealing(rectangles, temperature=10000, cooling_rate=0.003):
    current_state = rectangles[:]
    best_state = current_state[:]
    best_area, _, _ = calculate_smallest_rectangle_area(best_state)

    def swap_random_rectangles():
        index1, index2 = random.sample(range(len(current_state)), 2)
        rect1, rect2 = current_state[index1], current_state[index2]
        saved_x1, saved_y1 = rect1.x, rect1.y
        saved_x2, saved_y2 = rect2.x, rect2.y

        swap_rectangles(rect1, rect2)

        if any(is_overlap(rect, placed_rect) for rect in (rect1, rect2) for placed_rect in current_state if placed_rect.placed and placed_rect != rect):
            swap_rectangles(rect1, rect2)
            rect1.x, rect1.y = saved_x1, saved_y1
            rect2.x, rect2.y = saved_x2, saved_y2

    def move_rectangle_to_free_spot(rectangle):
        saved_x, saved_y = rectangle.x, rectangle.y
        free_spots = []

        for y in range(height - rectangle.height + 1):
            for x in range(width - rectangle.width + 1):
                if move_rectangle(x, y, rectangle, current_state):
                    free_spots.append((x, y))
                    rectangle.x = saved_x
                    rectangle.y = saved_y

        if free_spots:
            new_x, new_y = random.choice(free_spots)
            move_rectangle(new_x, new_y, rectangle, current_state)
        else:
            flip(rectangle)
            for y in range(height - rectangle.height + 1):
                for x in range(width - rectangle.width + 1):
                    if move_rectangle(x, y, rectangle, current_state):
                        free_spots.append((x, y))
                        rectangle.x = saved_x
                        rectangle.y = saved_y
    with open('testowanie.txt', 'w') as file:
        while temperature > 4.5:
            if random.random() < 0.5:  # Swap two random rectangles
                swap_random_rectangles()

            else:  # Move random rectangle to a different "free" spot
                index = random.randint(0, len(current_state) - 1)
                rectangle = current_state[index]
                start_time = time.time()
                if time.time() - start_time > 1:  # Check if time exceeds 1 minute
                    move_rectangle_to_free_spot(rectangle,current_state)

            current_area, _, _ = calculate_smallest_rectangle_area(current_state)

            if current_area < best_area or random.random() < math.exp((best_area - current_area) / temperature):
                best_state = current_state[:]
                best_area = current_area
                temperature *= 1 - cooling_rate

    return best_state

rectangles = read_rectangles_from_file('tiles.txt')
initial_canvas, width, height = find_non_overlapping_arrangement(rectangles)
initial_smallest_area, initial_top_right, initial_empty_percentage = calculate_smallest_rectangle_area(rectangles)
print("Initial Area of Smallest Rectangle:", initial_smallest_area)
print("Initial Top-Right Coordinate:", initial_top_right)
print("Initial Empty Percentage:", initial_empty_percentage)
plot_rectangles(rectangles)

best_state = simulated_annealing(rectangles)
final_canvas, final_top_right, final_empty_percentage = calculate_smallest_rectangle_area(best_state)
print("Final Area of Smallest Rectangle:", final_canvas)
print("Final Top-Right Coordinate:", final_top_right)
print("Final Empty Percentage:", final_empty_percentage)

save_results_to_file(best_state)
plot_rectangles(best_state)
