import sys
import os
import yaml
import pandas as pd
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QFormLayout, 
                             QDoubleSpinBox, QCheckBox, QComboBox, QLabel, QFileDialog,
                             QProgressBar, QMessageBox)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 1. The Worker Object (Handles the heavy lifting) ---
class SimWorker(QObject):
    finished = Signal(dict)  # Signal to send results back to UI
    progress = Signal(str)   # Signal to send status updates

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        try:
            self.progress.emit("Simulation started...")
            # Import your existing logic here
            # from TransplantPolicySimulator.Driver import _run_and_analyse_sim
            # outdir = _run_and_analyse_sim(self.params)
            
            # Simulated result for structure demonstration
            results = {"status": "success", "outdir": "some/path"}
            self.finished.emit(results)
        except Exception as e:
            self.finished.emit({"status": "error", "message": str(e)})

# --- 2. The Main Window ---
class TransplantSimApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transplant Policy Simulator")
        self.resize(1100, 800)

        # Set Global White Theme
        self.setStyleSheet("""
            QMainWindow { background-color: white; }
            QWidget { background-color: white; }
            QTabWidget::pane { border: 1px solid #ccc; background: white; }
            QPushButton { padding: 8px; border-radius: 4px; border: 1px solid #ccc; background-color: #f0f0f0; }
            QPushButton:hover { background-color: #e0e0e0; }
            QHeaderView::section { background-color: #f0f0f0; padding: 4px; border: 1px solid #ccc; }
        """)     

        # Main Layout
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create Tabs
        self.setup_sim_tab()
        self.setup_compare_tab()
        self.setup_docs_tab()

    def setup_policy_builder_tab(self):
        """Replaces the 'Policy Builder' nav_panel with a dynamic table builder."""
        vars_list = ["age", "height_delta", "waitlist_days", "blood_group"]
        tab = PolicyBuilderTab(vars_list)
        self.tabs.addTab(tab, "Policy Builder")

    def setup_sim_tab(self):
        """Replaces the 'Run Simulations' nav_panel"""
        tab = QWidget()
        layout = QHBoxLayout()

        # Left Sidebar: Configuration
        sidebar = QVBoxLayout()
        self.config_form = QFormLayout()
        
        # Example of dynamic parameter loading from your data_config.yml
        self.add_config_row("Years", QDoubleSpinBox(), 20)
        self.add_config_row("Policy", QComboBox(), ["ALLOCATION_SCORE", "RISK_ADJUSTED_BENEFIT"])
        
        self.run_btn = QPushButton("Run Simulation")
        self.run_btn.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")
        self.run_btn.clicked.connect(self.start_simulation)
        
        sidebar.addLayout(self.config_form)
        sidebar.addWidget(self.run_btn)
        sidebar.addStretch()

        # Right Side: Results and Plots
        content = QVBoxLayout()
        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        
        # Matplotlib Canvas (Replaces output_widget)
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.set_title("Simulation Results Overview")
        
        content.addWidget(self.status_label)
        content.addWidget(self.progress_bar)
        content.addWidget(self.canvas)

        layout.addLayout(sidebar, 1)
        layout.addLayout(content, 3)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Run Simulation")

    def add_config_row(self, label, widget, default):
        if isinstance(widget, QDoubleSpinBox):
            widget.setValue(default)
        elif isinstance(widget, QComboBox):
            widget.addItems(default)
        self.config_form.addRow(label, widget)

    def setup_compare_tab(self):
        """Replaces 'Compare Simulations'"""
        tab = QWidget()
        layout = QVBoxLayout()
        btn = QPushButton("Select CSV Results to Compare")
        btn.clicked.connect(self.load_files_dialog)
        layout.addWidget(btn)
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Compare Simulations")

    def setup_docs_tab(self):
        """Replaces the iframe User Guide"""
        tab = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Documentation can be viewed in your browser for security.")
        btn = QPushButton("Open User Guide (Local HTML)")
        btn.clicked.connect(lambda: os.startfile("site/index.html")) # Native Windows call
        layout.addWidget(label)
        layout.addWidget(btn)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "User Guide")

    # --- Controller Logic (Replacing Shiny Server) ---

    def load_files_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Simulation Results", "", "CSV Files (*.csv)")
        if files:
            for file in files:
                df = pd.read_csv(resource_path(file))
                # Here you would add logic to display the data in a table or plot it
                print(f"Loaded {file} with shape {df.shape}")

            QMessageBox.information(self, "Files Loaded", f"Loaded {len(files)} files.")

    def start_simulation(self):
        # 1. Collect params from UI
        params = {"years": 20} # In reality, pull from widgets
        
        # 2. Setup Threading
        self.thread = QThread()
        self.worker = SimWorker(params)
        self.worker.moveToThread(self.thread)
        
        # 3. Connect Signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.handle_results)
        self.worker.progress.connect(self.status_label.setText)
        
        self.run_btn.setEnabled(False)
        self.thread.start()

    def handle_results(self, results):
        self.run_btn.setEnabled(True)
        if results.get("status") == "success":
            self.status_label.setText("Success! Results saved.")
            # Trigger your matplotlib plotting logic here
            self.ax.plot([1, 2, 3], [4, 5, 6]) # Example
            self.canvas.draw()
        else:
            QMessageBox.critical(self, "Error", results.get("message"))

class PolicyBuilderTab(QWidget):
    def __init__(self, vars_available):
        super().__init__()
        self.vars_available = vars_available
        self.layout = QVBoxLayout()

        # 1. The Table Builder
        self.table = QTableWidget(0, 5) # 0 rows to start, 5 columns
        self.table.setHorizontalHeaderLabels(["Coeff", "Op", "Variable", "Condition", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 2. Buttons to Manage Rows
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+ Add Term")
        self.remove_btn = QPushButton("- Remove Selected")
        self.add_btn.clicked.connect(self.add_term_row)
        self.remove_btn.clicked.connect(self.remove_term_row)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)

        # 3. Live Code Preview (Replaces output_code)
        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setPlaceholderText("Generated Python code will appear here...")
        self.code_preview.setMaximumHeight(150)
        self.code_preview.setStyleSheet("background-color: #f8f9fa; font-family: 'Courier New';")

        self.layout.addWidget(QLabel("<b>Policy Function Terms:</b>"))
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(self.table)
        self.layout.addWidget(QLabel("<b>Generated Code:</b>"))
        self.layout.addWidget(self.code_preview)
        
        self.setLayout(self.layout)

    def add_term_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Coefficient (Spinbox)
        coeff_spin = QDoubleSpinBox()
        coeff_spin.setRange(-1000, 1000)
        coeff_spin.setValue(1.0)
        coeff_spin.valueChanged.connect(self.update_code_preview)
        self.table.setCellWidget(row, 0, coeff_spin)

        # Operator (ComboBox)
        op_combo = QComboBox()
        op_combo.addItems(["*", "+", "-"])
        op_combo.currentTextChanged.connect(self.update_code_preview)
        self.table.setCellWidget(row, 1, op_combo)

        # Variable (ComboBox)
        var_combo = QComboBox()
        var_combo.addItems(self.vars_available)
        var_combo.currentTextChanged.connect(self.update_code_preview)
        self.table.setCellWidget(row, 2, var_combo)

        # Condition (ComboBox)
        cond_combo = QComboBox()
        cond_combo.addItems(["None", "==", ">", "<"])
        cond_combo.currentTextChanged.connect(self.update_code_preview)
        self.table.setCellWidget(row, 3, cond_combo)

        self.update_code_preview()

    def remove_term_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            self.update_code_preview()

    def update_code_preview(self):
        """Logic to build the string, mimicking your 'generated_policy_code' function"""
        code_lines = ["def allocation(Allocation, waitlist, donor, **kwargs):", "    allocated = "]
        terms = []
        
        for i in range(self.table.rowCount()):
            coeff = self.table.cellWidget(i, 0).value()
            op = self.table.cellWidget(i, 1).currentText()
            var = self.table.cellWidget(i, 2).currentText()
            cond = self.table.cellWidget(i, 3).currentText()
            
            term_str = f"{coeff} {op} {var}"
            if cond != "None":
                term_str = f"{coeff} * ({var} {cond} 'value')"
            
            terms.append(term_str)
        
        full_code = code_lines[0] + "\n" + code_lines[1] + " + ".join(terms) + "\n    return allocated"
        self.code_preview.setText(full_code)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransplantSimApp()
    window.show()
    sys.exit(app.exec())