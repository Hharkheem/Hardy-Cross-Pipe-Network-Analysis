import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HardyCrossApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hardy-Cross Pipe Network Analysis")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f8ff")
        
        # Set application icon
        try:
            self.root.iconbitmap("pipe_icon.ico")
        except:
            pass
        
        # Initialize variables
        self.pipes = []
        self.iterations = []
        self.current_iteration = 0
        self.n_pipes = 4
        self.n = 1.85  # Exponent for Hazen-Williams formula
        
        # Create main frames
        self.input_frame = ttk.LabelFrame(root, text="Pipe Network Input", padding=10)
        self.input_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.calculation_frame = ttk.LabelFrame(root, text="Calculation Results", padding=10)
        self.calculation_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create input widgets
        self.create_input_widgets()
        self.create_calculation_widgets()
        
        # Load example data
        self.load_example_data()
    
    def create_input_widgets(self):
        # Control buttons
        control_frame = ttk.Frame(self.input_frame)
        control_frame.pack(fill="x", pady=5)
        
        ttk.Button(control_frame, text="Add Pipe", command=self.add_pipe).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Remove Pipe", command=self.remove_pipe).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Clear All", command=self.clear_pipes).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Load Example", command=self.load_example_data).pack(side="left", padx=5)
        
        # Pipe input table
        table_frame = ttk.Frame(self.input_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Create scrollable frame for pipe table
        canvas = tk.Canvas(table_frame)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create headers 
        headers = [
            "Pipe", "Length (m)", "Diameter (m)", 
            "Flowrate (m³/min)", "Direction"
        ]
        
        for col, header in enumerate(headers):
            label = ttk.Label(self.scrollable_frame, text=header, font=("Arial", 10, "bold"))
            label.grid(row=0, column=col, padx=5, pady=2, sticky="ew")
        
        # Create initial pipe rows
        self.pipe_rows = []
        for i in range(self.n_pipes):
            self.add_pipe_row(i)
        
        # Run button
        run_frame = ttk.Frame(self.input_frame)
        run_frame.pack(fill="x", pady=10)
        
        ttk.Button(run_frame, text="Run Analysis", command=self.run_analysis, 
                  style="Accent.TButton").pack(side="right", padx=5)
        
        # Tolerance input
        tol_frame = ttk.Frame(run_frame)
        tol_frame.pack(side="right", padx=10)
        
        ttk.Label(tol_frame, text="Tolerance (m³/min):").pack(side="left")
        self.tolerance_var = tk.DoubleVar(value=0.2)
        ttk.Entry(tol_frame, textvariable=self.tolerance_var, width=8).pack(side="left", padx=5)
    
    def add_pipe_row(self, idx):
        row = []
        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.grid(row=idx+1, column=0, columnspan=5, sticky="ew", pady=2)  # columnspan=5 now
        
        # Pipe label
        pipe_label = ttk.Label(row_frame, text=f"Pipe {idx+1}")
        pipe_label.pack(side="left", padx=5)
        row.append(pipe_label)
        
        # Length entry
        length_var = tk.DoubleVar()
        length_entry = ttk.Entry(row_frame, textvariable=length_var, width=10)
        length_entry.pack(side="left", padx=5)
        row.append(length_var)
        
        # Diameter entry
        diam_var = tk.DoubleVar()
        diam_entry = ttk.Entry(row_frame, textvariable=diam_var, width=10)
        diam_entry.pack(side="left", padx=5)
        row.append(diam_var)
        
        # Initial flow entry 
        flow_var = tk.DoubleVar()
        flow_entry = ttk.Entry(row_frame, textvariable=flow_var, width=10)
        flow_entry.pack(side="left", padx=5)
        row.append(flow_var)
        
        # Direction combobox
        direction_var = tk.StringVar(value="Clockwise")
        direction_combo = ttk.Combobox(row_frame, textvariable=direction_var, 
                                      values=["Clockwise", "Counter-Clockwise"], width=15)
        direction_combo.pack(side="left", padx=5)
        # direction_combo.grid(row=0, column=4, padx=5, sticky="ew")
        row.append(direction_var)
        
        self.pipe_rows.append(row)
    
    def add_pipe(self):
        self.n_pipes += 1
        self.add_pipe_row(self.n_pipes - 1)
    
    def remove_pipe(self):
        if self.n_pipes > 2:
            # Get the last row and destroy its widgets
            last_row = self.pipe_rows.pop()
            for widget in last_row:
                if isinstance(widget, ttk.Label) or isinstance(widget, ttk.Frame):
                    widget.destroy()
            self.n_pipes -= 1
        else:
            messagebox.showwarning("Warning", "At least 2 pipes are required")
    
    def clear_pipes(self):
        for row in self.pipe_rows:
            # Skip the label widget when clearing
            row[1].set(0)  # Length
            row[2].set(0)  # Diameter
            row[3].set(0)  # Initial flow
            row[4].set("Clockwise")  # Reset direction to clockwise
    
    def load_example_data(self):
        # Clear any existing pipes beyond 4
        while self.n_pipes > 4:
            self.remove_pipe()
        
        # Set example values 
        example_data = [
            [500, 0.2, 1.0, "Clockwise"],    # Pipe AB
            [330, 0.35, 11.0, "Counter-Clockwise"],    # Pipe AC
            [330, 0.2, 0.5, "Clockwise"], # Pipe BD
            [500, 0.2, 1.0, "Counter-Clockwise"] # Pipe CD
        ]
        
        for i, data in enumerate(example_data):
            if i < self.n_pipes:
                self.pipe_rows[i][1].set(data[0])  # Length
                self.pipe_rows[i][2].set(data[1])  # Diameter
                self.pipe_rows[i][3].set(data[2])  # Initial flow
                self.pipe_rows[i][4].set(data[3])  # Direction
    
    def create_calculation_widgets(self):
        # Create notebook for iterations and results
        self.results_notebook = ttk.Notebook(self.calculation_frame)
        self.results_notebook.pack(fill="both", expand=True)
        
        # Iterations tab
        self.iterations_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.iterations_frame, text="Iterations")
        
        # Create text widget for iterations
        self.iterations_text = scrolledtext.ScrolledText(
            self.iterations_frame, wrap=tk.WORD, width=120, height=15
        )
        self.iterations_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.iterations_text.config(state=tk.DISABLED)
        
        # Results tab
        self.results_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.results_frame, text="Final Results")
        
        # Create text widget for final results
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame, wrap=tk.WORD, width=120, height=15
        )
        self.results_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.results_text.config(state=tk.DISABLED)
    
    
    def run_analysis(self):
        # Validate input
        if not self.validate_input():
            return
        
        # Collect pipe data
        self.pipes = []
        for i, row in enumerate(self.pipe_rows):
            pipe_data = {
                'name': f"Pipe {i+1}",
                'length': row[1].get(),
                'diameter': row[2].get(),
                'C': 100,  # Constant C value
                'initial_flow': row[3].get(),  
                'direction': 1 if row[4].get() == "Clockwise" else -1  
            }
            pipe_data['flow'] = pipe_data['initial_flow'] * pipe_data['direction']
            self.pipes.append(pipe_data)
        
        # Calculate K values
        for pipe in self.pipes:
            L = pipe['length']
            d = pipe['diameter']
            C = pipe['C']
            num = 10.67 * L
            denom = (C ** 1.85) * (d ** 4.87)
            pipe['K'] = num / denom
        
        # Run Hardy-Cross iterations
        self.iterations = []
        tolerance = self.tolerance_var.get()
        max_iter = 50
        iter_count = 0
        q = 1000.0  # initial large value
        
        while abs(q) > tolerance and iter_count < max_iter:
            iter_count += 1
            iteration_data = {
                'number': iter_count,
                'pipes': [],
                'sum_hl': 0,
                'sum_abs_hl_over_Q': 0,
                'q': 0
            }
            
            # Calculate head loss and other values for each pipe
            for pipe in self.pipes:
                pipe_data = {}
                
                # Current flow in m³/min and m³/s
                pipe_data['flow_min'] = pipe['flow']
                pipe_data['flow_s'] = pipe['flow'] / 60.0
                
                # Head loss calculation
                sign = 1 if pipe['flow'] >= 0 else -1
                pipe_data['hl'] = sign * pipe['K'] * abs(pipe_data['flow_s']) ** self.n
                
                # |h_l|/|Q| calculation
                if abs(pipe_data['flow_s']) > 1e-6:
                    pipe_data['abs_hl_over_Q'] = abs(pipe_data['hl']) / abs(pipe_data['flow_s'])
                else:
                    pipe_data['abs_hl_over_Q'] = 0
                
                # Add to iteration data
                iteration_data['pipes'].append(pipe_data)
                iteration_data['sum_hl'] += pipe_data['hl']
                iteration_data['sum_abs_hl_over_Q'] += pipe_data['abs_hl_over_Q']
            
            # Calculate correction factor
            n = self.n
            if iteration_data['sum_abs_hl_over_Q'] > 0:
                q_s = -iteration_data['sum_hl'] / (n * iteration_data['sum_abs_hl_over_Q'])
                q = q_s * 60.0  # Convert to m³/min
            else:
                q = 0
                
            iteration_data['q'] = q
            
            # Apply correction to flows
            for pipe, pipe_data in zip(self.pipes, iteration_data['pipes']):
                pipe['flow'] += q
            
            # Save iteration
            self.iterations.append(iteration_data)
        
        # Display results
        self.display_iterations()
        self.display_final_results()
        
    
    def validate_input(self):
        for row in self.pipe_rows:
            # Check length
            if row[1].get() <= 0:
                messagebox.showerror("Input Error", "Pipe length must be positive")
                return False
            
            # Check diameter
            if row[2].get() <= 0:
                messagebox.showerror("Input Error", "Pipe diameter must be positive")
                return False
            
            # Check flow rate (index changed from 4 to 3)
            if row[3].get() < 0:
                messagebox.showerror("Input Error", "Flow rate must be non-negative")
                return False
        
        # Check tolerance
        if self.tolerance_var.get() <= 0:
            messagebox.showerror("Input Error", "Tolerance must be positive")
            return False
            
        return True
    
    def display_iterations(self):
        self.iterations_text.config(state=tk.NORMAL)
        self.iterations_text.delete(1.0, tk.END)
        
        for iteration in self.iterations:
            self.iterations_text.insert(tk.END, f"\nIteration {iteration['number']}:\n")
            self.iterations_text.insert(tk.END, "-"*120 + "\n")
            # Removed C value from header
            self.iterations_text.insert(tk.END, 
                f"{'Pipe':<10}{'Length':>10}{'Diameter':>12}{'Flow (m³/min)':>15}{'Flow (m³/s)':>15}{'K':>15}{'h_l (m)':>15}{'|h_l|/|Q|':>15}\n")
            
            for i, pipe in enumerate(iteration['pipes']):
                pipe_data = self.pipes[i]
                self.iterations_text.insert(tk.END, 
                    f"{pipe_data['name']:<10}"
                    f"{pipe_data['length']:>10.1f}"
                    f"{pipe_data['diameter']:>12.3f}"
                    f"{pipe['flow_min']:>15.4f}"
                    f"{pipe['flow_s']:>15.6f}"
                    f"{pipe_data['K']:>15.4f}"
                    f"{pipe['hl']:>15.4f}"
                    f"{pipe['abs_hl_over_Q']:>15.4f}\n")
            
            self.iterations_text.insert(tk.END, "\n")
            self.iterations_text.insert(tk.END, f"Sum of head losses (Σ h_l) = {iteration['sum_hl']:.4f} m\n")
            self.iterations_text.insert(tk.END, f"Sum of |h_l|/|Q| = {iteration['sum_abs_hl_over_Q']:.4f}\n")
            self.iterations_text.insert(tk.END, f"Correction (q) = {iteration['q']:.6f} m³/min\n")
            self.iterations_text.insert(tk.END, "-"*120 + "\n")
        
        self.iterations_text.config(state=tk.DISABLED)
    
    def display_final_results(self):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        self.results_text.insert(tk.END, "Hardy-Cross Method Results\n")
        self.results_text.insert(tk.END, "="*80 + "\n\n")
        
        # Display pipe results (removed C value)
        self.results_text.insert(tk.END, f"{'Pipe':<10}{'Length':>10}{'Diameter':>12}{'Flow (m³/min)':>15}{'Direction':>15}\n")
        self.results_text.insert(tk.END, "-"*80 + "\n")
        
        for pipe in self.pipes:
            direction = "Clockwise" if pipe['direction'] == 1 else "Counter-Clockwise"
            flow = pipe['flow'] * pipe['direction']
            
            self.results_text.insert(tk.END, 
                f"{pipe['name']:<10}"
                f"{pipe['length']:>10.1f}"
                f"{pipe['diameter']:>12.3f}"
                f"{abs(flow):>15.4f}"
                f"{direction:>15}\n")
        
        self.results_text.insert(tk.END, "\n")
        self.results_text.insert(tk.END, f"Converged in {len(self.iterations)} iterations\n")
        self.results_text.insert(tk.END, f"Final correction: {self.iterations[-1]['q']:.6f} m³/min\n")
        
        # Calculate total head loss
        total_hl = 0
        for pipe in self.pipes:
            flow_s = pipe['flow'] / 60.0
            sign = 1 if pipe['flow'] >= 0 else -1
            hl = sign * pipe['K'] * (abs(flow_s)) ** self.n
            total_hl += hl
        
        self.results_text.insert(tk.END, f"Total head loss: {total_hl:.4f} m\n")
        
        self.results_text.config(state=tk.DISABLED)
    

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Accent.TButton', foreground='white', background='#4a7abc', font=('Arial', 10, 'bold'))
    app = HardyCrossApp(root)
    root.mainloop()