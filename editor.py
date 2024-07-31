import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json
from tile import create_tiles, Tile


class TileGridUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Tile Grid UI")
        self.tiles = create_tiles()
        self.grid_width = tk.IntVar(value=5)
        self.grid_height = tk.IntVar(value=5)
        self.grid = []
        self.selected_tile_type = tk.StringVar()
        self.tile_images = {}  # Dictionary to store tile images
        # Store the destination point (x, y) where x is column and y is row
        self.destination = None
        self.setup_ui()
        self.initialize_grid()

    def setup_ui(self):
        # Grid size configuration
        ttk.Label(self.master, text="Grid Width:").grid(
            row=0, column=0, padx=5, pady=5)
        ttk.Entry(self.master, textvariable=self.grid_width,
                  width=5).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.master, text="Grid Height:").grid(
            row=0, column=2, padx=5, pady=5)
        ttk.Entry(self.master, textvariable=self.grid_height,
                  width=5).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(self.master, text="Set Grid Size", command=self.initialize_grid).grid(
            row=0, column=4, padx=5, pady=5)

        # Tile selection
        ttk.Label(self.master, text="Select Tile Type:").grid(
            row=1, column=0, padx=5, pady=5)
        tile_options = [
            f"{tile.name} (Index: {tile.index})" for tile in self.tiles]
        self.tile_combobox = ttk.Combobox(
            self.master, textvariable=self.selected_tile_type, values=tile_options, state="readonly")
        self.tile_combobox.grid(
            row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        self.tile_combobox.bind("<<ComboboxSelected>>", self.on_tile_selected)

        # Set Destination button
        self.set_destination_button = ttk.Button(
            self.master, text="Set Destination", command=self.toggle_set_destination)
        self.set_destination_button.grid(row=1, column=4, padx=5, pady=5)
        self.setting_destination = False

        # Save and Load buttons
        ttk.Button(self.master, text="Save Grid", command=self.save_grid).grid(
            row=2, column=0, padx=5, pady=5)
        ttk.Button(self.master, text="Load Grid", command=self.load_grid).grid(
            row=2, column=1, padx=5, pady=5)

        # Grid canvas
        self.canvas_frame = ttk.Frame(self.master)
        self.canvas_frame.grid(row=3, column=0, columnspan=5, padx=5, pady=5)
        self.canvas = tk.Canvas(
            self.canvas_frame, width=400, height=400, bg="white")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def initialize_grid(self):
        self.grid = [[0 for _ in range(self.grid_width.get())]
                     for _ in range(self.grid_height.get())]
        self.destination = None
        self.update_canvas_size()
        self.draw_grid()

    def update_canvas_size(self):
        max_width = 800  # Maximum width of the canvas
        max_height = 600  # Maximum height of the canvas
        aspect_ratio = self.grid_width.get() / self.grid_height.get()

        if aspect_ratio > max_width / max_height:
            canvas_width = max_width
            canvas_height = int(max_width / aspect_ratio)
        else:
            canvas_height = max_height
            canvas_width = int(max_height * aspect_ratio)

        self.canvas.config(width=canvas_width, height=canvas_height)
        self.master.update_idletasks()  # Update the window to reflect size changes

    def draw_grid(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cell_width = canvas_width // self.grid_width.get()
        cell_height = canvas_height // self.grid_height.get()

        for row in range(self.grid_height.get()):
            for col in range(self.grid_width.get()):
                x1, y1 = col * cell_width, row * cell_height
                x2, y2 = x1 + cell_width, y1 + cell_height
                tile_index = self.grid[row][col]
                tile_image = self.get_tile_image(
                    tile_index, (cell_width, cell_height))
                self.canvas.create_image(x1, y1, anchor="nw", image=tile_image)
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="gray")

                # Draw destination marker
                # Changed from (row, col) to (col, row)
                if self.destination and self.destination == (col, row):
                    self.canvas.create_oval(
                        x1+40, y1+40, x2-40, y2-40, fill="green", outline="green")

    def get_tile_image(self, tile_index, size):
        if (tile_index, size) not in self.tile_images:
            tile = self.tiles[tile_index]
            img = tile.img.copy()
            img = img.resize(size, Image.LANCZOS)
            photo_image = ImageTk.PhotoImage(img)
            self.tile_images[(tile_index, size)] = photo_image
        return self.tile_images[(tile_index, size)]

    def on_tile_selected(self, event):
        selected_tile = self.tile_combobox.get()
        self.selected_tile_index = int(
            selected_tile.split("Index: ")[1].rstrip(")"))

    def toggle_set_destination(self):
        self.setting_destination = not self.setting_destination
        if self.setting_destination:
            self.set_destination_button.config(text="Cancel Set Destination")
        else:
            self.set_destination_button.config(text="Set Destination")

    def on_canvas_click(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cell_width = canvas_width // self.grid_width.get()
        cell_height = canvas_height // self.grid_height.get()
        col = event.x // cell_width
        row = event.y // cell_height

        if self.setting_destination:
            # Changed from (row, col) to (col, row)
            self.destination = (col, row)
            self.toggle_set_destination()
        elif hasattr(self, 'selected_tile_index'):
            self.grid[row][col] = self.selected_tile_index
        else:
            messagebox.showwarning(
                "No Tile Selected", "Please select a tile type before clicking on the grid.")

        self.draw_grid()

    def save_grid(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            data = {
                "grid": self.grid,
                "destination": self.destination
            }
            with open(file_path, 'w') as f:
                json.dump(data, f)
            messagebox.showinfo("Save Successful",
                                "Grid and destination saved successfully!")

    def load_grid(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.grid = data["grid"]
            self.destination = tuple(
                data["destination"]) if data["destination"] else None
            self.grid_height.set(len(self.grid))
            self.grid_width.set(len(self.grid[0]))
            self.update_canvas_size()
            self.draw_grid()
            messagebox.showinfo("Load Successful",
                                "Grid and destination loaded successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = TileGridUI(root)
    root.mainloop()
