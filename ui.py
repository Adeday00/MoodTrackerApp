import tkinter as tk
from tkinter import messagebox, Scrollbar, Frame, Text, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
import database

LIGHT_MODE = {
    "bg": "#ffffff",
    "fg": "#333333",
    "button_bg": "#4CAF50",
    "button_fg": "#000000",
    "entry_bg": "#f9f9f9",
    "history_button_bg": "#2196F3",
    "graph_bg": "#ffffff",
    "graph_color": "skyblue",
    "button_active_bg": "#45a049"
}

DARK_MODE = {
    "bg": "#2d2d2d",
    "fg": "#ffffff",
    "button_bg": "#4CAF50",
    "button_fg": "#000000",
    "entry_bg": "#3d3d3d",
    "history_button_bg": "#2196F3",
    "graph_bg": "#2d2d2d",
    "graph_color": "#4a9eff",
    "button_active_bg": "#45a049"
}

def validate_mood(mood_str):
    """Validate mood input is between 1-5"""
    try:
        mood = int(mood_str)
        return 1 <= mood <= 5
    except ValueError:
        return False

def save_mood():
    date = datetime.now().strftime("%A, %Y-%m-%d %I:%M %p")
    mood = mood_entry.get().strip()
    notes = notes_entry.get("1.0", tk.END).strip()
    
    if not mood:
        messagebox.showerror("Error", "Please enter a mood rating.")
        return
        
    if not validate_mood(mood):
        messagebox.showerror("Error", "Please enter a mood rating between 1 and 5.")
        return

    try:
        database.add_mood(date, int(mood), notes)
        messagebox.showinfo("Success", "Mood entry saved successfully!")
        mood_entry.delete(0, tk.END)
        notes_entry.delete("1.0", tk.END)
        display_moods()  # Refresh the display after saving
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save mood: {str(e)}")

def display_moods():
    moods = database.get_moods()
    show_mood_graph(moods)

def toggle_theme():
    current_bg = root.cget("bg")
    is_light = current_bg == LIGHT_MODE["bg"]
    theme = DARK_MODE if is_light else LIGHT_MODE
    
    # Update main window
    root.config(bg=theme["bg"])
    
    # Update labels
    for widget in [title_label, mood_label, notes_label]:
        widget.config(bg=theme["bg"], fg=theme["fg"])
    
    # Update mood guide frame and its labels
    mood_guide_frame.config(bg=theme["bg"])
    for label in mood_guide_frame.winfo_children():
        label.config(bg=theme["bg"], fg=theme["fg"])
    
    # Update entry fields
    mood_entry.config(bg=theme["entry_bg"], fg=theme["fg"])
    notes_entry.config(bg=theme["entry_bg"], fg=theme["fg"])
    
    # Update buttons
    save_button.config(
        bg=theme["button_bg"], 
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"],
        activeforeground=theme["button_fg"]
    )
    history_button.config(
        bg=theme["history_button_bg"], 
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"],
        activeforeground=theme["button_fg"]
    )
    theme_button.config(
        bg=theme["button_bg"], 
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"],
        activeforeground=theme["button_fg"]
    )
    
    # Update graph frame
    graph_frame.config(bg=theme["bg"])
    
    # Refresh graph if it exists
    if len(graph_frame.winfo_children()) > 0:
        display_moods()

def show_mood_graph(moods):
    # Group moods by date and calculate daily average mood
    daily_moods = defaultdict(list)
    for entry in moods:
        try:
            date_str = entry[1]  # Get the full date string
            if len(date_str.split()) > 1:
                date = datetime.strptime(date_str.split()[1], "%Y-%m-%d").date()
                daily_moods[date].append(entry[2])
            else:
                print(f"Skipping entry due to unexpected date format: {date_str}")
        except (IndexError, ValueError) as e:
            print("Error parsing date:", e, "for entry:", entry)
            continue

    # Calculate daily averages for the last 7 days
    sorted_dates = sorted(daily_moods.keys())[-7:]  # Get the last 7 unique days
    dates = []
    average_moods = []

    for date in sorted_dates:
        avg_mood = sum(daily_moods[date]) / len(daily_moods[date])
        dates.append(date.strftime("%a"))  # Format date as abbreviated weekday name
        average_moods.append(avg_mood)

    # Check if we have data to plot
    if not dates or not average_moods:
        print("No data to display on the graph.")
        return

    # Clear previous graph
    for widget in graph_frame.winfo_children():
        widget.destroy()

    # Get current theme
    is_light = root.cget("bg") == LIGHT_MODE["bg"]
    theme = LIGHT_MODE if is_light else DARK_MODE

    # Plot the average mood for the last 7 days as a bar chart
    fig, ax = plt.subplots(figsize=(5, 3))
    fig.patch.set_facecolor(theme["bg"])
    ax.set_facecolor(theme["bg"])
    
    bars = ax.bar(dates, average_moods, color=theme["graph_color"])
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom',
                color=theme["fg"])

    ax.set_ylim(0.5, 5.5)
    ax.grid(True, axis='y', linestyle='--', alpha=0.3, color='gray')
    ax.set_title("Average Mood Over Last 7 Days", pad=10, color=theme["fg"])
    ax.set_xlabel("Day of the Week", color=theme["fg"])
    ax.set_ylabel("Average Mood", color=theme["fg"])

    # Style the ticks
    ax.tick_params(colors=theme["fg"])
    for spine in ax.spines.values():
        spine.set_color(theme["fg"])

    # Embed the figure
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    plt.close(fig)

# Setting up the main application window
root = tk.Tk()
root.title("Mood Tracker")
root.geometry("600x800")
root.config(bg="#ffffff")

# Title Label
title_label = tk.Label(root, text="Mood Tracker", font=("Helvetica", 16, "bold"), bg="#ffffff", fg="#333333")
title_label.pack(pady=10)

# Mood Rating Input
mood_label = tk.Label(root, text="Mood Rating (1-5):", font=("Helvetica", 12), bg="#ffffff", fg="#333333")
mood_label.pack(pady=5)

mood_guide_frame = tk.Frame(root, bg=LIGHT_MODE["bg"])
mood_guide_frame.pack(pady=2)

mood_ratings = {
    "5": "Very Happy 😊",
    "4": "Happy 🙂",
    "3": "Neutral 😐",
    "2": "Sad 😔",
    "1": "Very Sad 😢"
}

for rating, description in mood_ratings.items():
    guide_text = f"{rating}: {description}"
    rating_label = tk.Label(
        mood_guide_frame, 
        text=guide_text,
        font=("Helvetica", 10),
        bg=LIGHT_MODE["bg"],
        fg=LIGHT_MODE["fg"]
    )
    rating_label.pack()

mood_entry = tk.Entry(root, font=("Helvetica", 12), width=10, justify="center", relief="solid", bd=1)
mood_entry.pack(pady=5)

# Notes Input
notes_label = tk.Label(root, text="Notes (optional):", font=("Helvetica", 12), bg="#ffffff", fg="#333333")
notes_label.pack(pady=5)
notes_entry = tk.Text(root, font=("Helvetica", 10), height=4, width=30, relief="solid", bd=1, bg="#f9f9f9", fg="#333333")
notes_entry.pack(pady=5)

# Save Button
save_button = tk.Button(
    root, 
    text="Save Mood", 
    font=("Helvetica", 12, "bold"), 
    bg=LIGHT_MODE["button_bg"], 
    fg=LIGHT_MODE["button_fg"],
    activebackground=LIGHT_MODE["button_bg"],
    activeforeground=LIGHT_MODE["button_fg"],
    width=15, 
    command=save_mood
)
save_button.pack(pady=10)

# View History Button
history_button = tk.Button(
    root, 
    text="View History", 
    font=("Helvetica", 12, "bold"), 
    bg=LIGHT_MODE["history_button_bg"], 
    fg=LIGHT_MODE["button_fg"],
    activebackground=LIGHT_MODE["button_bg"],
    activeforeground=LIGHT_MODE["button_fg"],
    width=15, 
    command=display_moods
)
history_button.pack(pady=10)

# Toggle Theme Button
theme_button = tk.Button(
    root, 
    text="Toggle Theme", 
    font=("Helvetica", 12, "bold"),
    bg=LIGHT_MODE["button_bg"], 
    fg=LIGHT_MODE["button_fg"],
    activebackground=LIGHT_MODE["button_bg"],
    activeforeground=LIGHT_MODE["button_fg"],
    width=15, 
    command=toggle_theme
)
theme_button.pack(pady=10)

# Graph Frame for Embedding the Graph
graph_frame = tk.Frame(root, bg="#ffffff")
graph_frame.pack(pady=10, fill="both", expand=True)

# Make the root window responsive to resizing
root.columnconfigure(0, weight=1)
root.rowconfigure(5, weight=1)
graph_frame.columnconfigure(0, weight=1)
graph_frame.rowconfigure(0, weight=1)

# Add tooltips
def create_tooltip(widget, text):
    def show_tooltip(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(tooltip, text=text, justify='left',
                        background="#ffffe0", relief='solid', borderwidth=1)
        label.pack()
        
        def hide_tooltip():
            tooltip.destroy()
            
        widget.tooltip = tooltip
        widget.bind('<Leave>', lambda e: hide_tooltip())
        
    widget.bind('<Enter>', show_tooltip)

# Add tooltips to widgets
create_tooltip(mood_entry, "Enter a number between 1 (lowest) and 5 (highest)")
create_tooltip(save_button, "Save your current mood (Ctrl+S)")
create_tooltip(history_button, "View your mood history (Ctrl+H)")
create_tooltip(theme_button, "Switch between light and dark mode (Ctrl+T)")

# Add keyboard shortcuts
root.bind('<Control-s>', lambda e: save_mood())
root.bind('<Control-h>', lambda e: display_moods())
root.bind('<Control-t>', lambda e: toggle_theme())
root.bind('<Return>', lambda e: save_mood())  # Enter key to save

# Focus on mood entry when starting
mood_entry.focus()

root.mainloop()
