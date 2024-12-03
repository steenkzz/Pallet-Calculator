import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QComboBox, QHBoxLayout, QCheckBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QMovie, QFont
import pyqtgraph.opengl as gl
import numpy as np
from box_visualization import create_box_mesh
from translations import translations

class PalletCalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pallet Calculator")
        self.setGeometry(100, 100, 800, 750)  # Increased height by 25%

        # Main container widget
        container = QWidget()
        self.setCentralWidget(container)

        # Layout
        self.layout = QVBoxLayout()

        # Horizontal layout for unit and language selection
        top_layout = QHBoxLayout()

        # Unit selection
        self.unit_input = QComboBox()
        self.unit_input.addItems(["MM", "CM", "INCH"])
        self.unit_input.setCurrentText("MM")
        self.unit_input.currentTextChanged.connect(self.change_units)
        top_layout.addWidget(QLabel("Unit:"))
        top_layout.addWidget(self.unit_input)

        # Language selection
        self.language_input = QComboBox()
        self.language_input.addItems(["English", "Dutch"])
        self.language_input.setCurrentText("English")
        self.language_input.currentTextChanged.connect(self.change_language)
        top_layout.addWidget(QLabel("Language:"))
        top_layout.addWidget(self.language_input)

        self.layout.addLayout(top_layout)

        # Form layout for input fields
        self.form_layout = QFormLayout()

        # Pallet dimensions
        self.pallet_size_input = QComboBox()
        self.pallet_size_input.addItems([
            "Europallet 1200 x 800",
            "Industrie 1200 x 1000",
            "Halfpallet 800 x 600",
            "40 x 48\" Pallet"
        ])
        self.form_layout.addRow("Pallet Size:", self.pallet_size_input)

        # Box 1 dimensions
        self.box1_length_input = QLineEdit()
        self.box1_width_input = QLineEdit()
        self.box1_height_input = QLineEdit()
        self.form_layout.addRow("Box 1 Length (mm):", self.box1_length_input)
        self.form_layout.addRow("Box 1 Width (mm):", self.box1_width_input)
        self.form_layout.addRow("Box 1 Height (mm):", self.box1_height_input)

        # Max loading height
        self.max_loading_height_input = QLineEdit()
        self.form_layout.addRow("Max Loading Height (mm):", self.max_loading_height_input)

        self.layout.addLayout(self.form_layout)

        # Box weight checkbox
        self.box_weight_checkbox = QCheckBox("Box Weight")
        self.box_weight_checkbox.stateChanged.connect(self.toggle_box_weight)
        self.layout.addWidget(self.box_weight_checkbox)

        # Add and Remove box buttons
        button_layout = QHBoxLayout()
        self.add_box_button = QPushButton("Add Box")
        self.add_box_button.clicked.connect(self.add_box)
        button_layout.addWidget(self.add_box_button)

        self.remove_box_button = QPushButton("Remove Box")
        self.remove_box_button.clicked.connect(self.remove_box)
        button_layout.addWidget(self.remove_box_button)

        self.layout.addLayout(button_layout)

        # Calculate button
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate_boxes)
        self.layout.addWidget(self.calculate_button)

        # Loading label for GIF
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_movie = QMovie("loading.gif")
        self.loading_label.setMovie(self.loading_movie)
        self.layout.addWidget(self.loading_label)
        self.loading_label.hide()

        # 3D view for result
        self.gl_view = gl.GLViewWidget()
        self.gl_view.setBackgroundColor('#F0F0F0')  # Set background color to hex code F0F0F0
        self.layout.addWidget(self.gl_view)
        self.gl_view.hide()

        # Result label
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Arial", 16))  # Set font size to 16
        self.layout.addWidget(self.result_label)
        self.result_label.hide()

        # Created by label
        self.created_by_label = QLabel("created by Martijn Steenks")
        self.created_by_label.setFont(QFont("Arial", 8))  # Set font size to 8
        self.created_by_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.layout.addWidget(self.created_by_label)

        # Set the layout
        container.setLayout(self.layout)

        # Set Enter key to trigger calculate button
        self.calculate_button.setDefault(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        # Initialize box count
        self.box_count = 1
        self.box_inputs = []
        self.box_weight_inputs = []

        # Initialize translations
        self.current_language = "English"
        self.change_language(self.current_language)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.calculate_button.click()

    def add_box(self):
        if self.box_count >= 5:
            QMessageBox.information(self, "Info", "No more box dimensions available")
            return

        self.box_count += 1
        box_length_input = QLineEdit()
        box_width_input = QLineEdit()
        box_height_input = QLineEdit()
        self.form_layout.insertRow(self.form_layout.rowCount() - 1, f"Box {self.box_count} Length ({self.unit_input.currentText().lower()}):", box_length_input)
        self.form_layout.insertRow(self.form_layout.rowCount() - 1, f"Box {self.box_count} Width ({self.unit_input.currentText().lower()}):", box_width_input)
        self.form_layout.insertRow(self.form_layout.rowCount() - 1, f"Box {self.box_count} Height ({self.unit_input.currentText().lower()}):", box_height_input)
        self.box_inputs.append((box_length_input, box_width_input, box_height_input))

        if self.box_weight_checkbox.isChecked():
            box_weight_input = QLineEdit()
            self.form_layout.insertRow(self.form_layout.rowCount() - 1, f"Box {self.box_count} Weight (kg):", box_weight_input)
            self.box_weight_inputs.append(box_weight_input)

    def remove_box(self):
        if self.box_count <= 1:
            QMessageBox.information(self, "Info", "No box dimensions to remove")
            return

        for _ in range(3):
            self.form_layout.removeRow(self.form_layout.rowCount() - 2)
        if self.box_weight_checkbox.isChecked():
            self.form_layout.removeRow(self.form_layout.rowCount() - 2)
            self.box_weight_inputs.pop()
        self.box_inputs.pop()
        self.box_count -= 1

    def toggle_box_weight(self, state):
        if state == Qt.Checked:
            # Add weight input for Box 1
            self.box1_weight_input = QLineEdit()
            self.form_layout.insertRow(6, "Box 1 Weight (kg):", self.box1_weight_input)
            # Add weight inputs for additional boxes
            for i in range(len(self.box_inputs)):
                box_weight_input = QLineEdit()
                self.form_layout.insertRow(self.form_layout.rowCount() - 1, f"Box {i + 2} Weight (kg):", box_weight_input)
                self.box_weight_inputs.append(box_weight_input)
        else:
            # Remove weight input for Box 1
            if hasattr(self, 'box1_weight_input'):
                self.form_layout.removeRow(self.form_layout.indexOf(self.box1_weight_input))
                del self.box1_weight_input
            # Remove weight inputs for additional boxes
            for _ in range(len(self.box_weight_inputs)):
                self.form_layout.removeRow(self.form_layout.rowCount() - 2)
            self.box_weight_inputs.clear()

    def change_units(self, unit):
        self.form_layout.labelForField(self.box1_length_input).setText(f"Box 1 Length ({unit.lower()}):")
        self.form_layout.labelForField(self.box1_width_input).setText(f"Box 1 Width ({unit.lower()}):")
        self.form_layout.labelForField(self.box1_height_input).setText(f"Box 1 Height ({unit.lower()}):")
        self.form_layout.labelForField(self.max_loading_height_input).setText(f"Max Loading Height ({unit.lower()}):")
        for i, (length_input, width_input, height_input) in enumerate(self.box_inputs):
            self.form_layout.labelForField(length_input).setText(f"Box {i + 2} Length ({unit.lower()}):")
            self.form_layout.labelForField(width_input).setText(f"Box {i + 2} Width ({unit.lower()}):")
            self.form_layout.labelForField(height_input).setText(f"Box {i + 2} Height ({unit.lower()}):")

    def calculate_boxes(self):
        try:
            # Show loading GIF
            self.loading_label.show()
            self.loading_movie.start()

            # Get pallet dimensions based on selection
            pallet_size = self.pallet_size_input.currentText()
            if pallet_size == "Europallet 1200 x 800":
                pallet_length, pallet_width = 1200, 800
            elif pallet_size == "Industrie 1200 x 1000":
                pallet_length, pallet_width = 1200, 1000
            elif pallet_size == "Halfpallet 800 x 600":
                pallet_length, pallet_width = 800, 600
            elif pallet_size == "40 x 48\" Pallet":
                pallet_length, pallet_width = 101.6, 121.9  # Converted to cm

            # Get box 1 dimensions
            box1_length = float(self.box1_length_input.text())
            box1_width = float(self.box1_width_input.text())
            box1_height = float(self.box1_height_input.text())
            box1_weight = float(self.box1_weight_input.text()) if self.box_weight_checkbox.isChecked() else 0

            # Get additional box dimensions
            additional_boxes = []
            total_weight = box1_weight
            for i, (length_input, width_input, height_input) in enumerate(self.box_inputs):
                length = float(length_input.text())
                width = float(width_input.text())
                height = float(height_input.text())
                weight = float(self.box_weight_inputs[i].text()) if self.box_weight_checkbox.isChecked() else 0
                additional_boxes.append((length, width, height, weight))
                total_weight += weight

            # Get max loading height
            max_loading_height = float(self.max_loading_height_input.text())

            # Scale down the boxes to fit within the view
            scale_factor = 0.3  # Adjusted scale factor to make the 3D image 30% smaller
            pallet_length *= scale_factor
            pallet_width *= scale_factor
            box1_length *= scale_factor
            box1_width *= scale_factor
            box1_height *= scale_factor
            max_loading_height *= scale_factor

            for i in range(len(additional_boxes)):
                additional_boxes[i] = tuple(dim * scale_factor if j < 3 else dim for j, dim in enumerate(additional_boxes[i]))

            # Debug print statements to verify scaling
            print(f"Scaled pallet dimensions: {pallet_length} x {pallet_width}")
            print(f"Scaled box 1 dimensions: {box1_length} x {box1_width} x {box1_height}")
            for i, (length, width, height, weight) in enumerate(additional_boxes):
                print(f"Scaled box {i + 2} dimensions: {length} x {width} x {height}")
            print(f"Scaled max loading height: {max_loading_height}")

            # Calculate number of boxes that fit on the pallet
            def calculate_boxes_per_pallet(pallet_length, pallet_width, box_length, box_width, box_height):
                boxes_per_layer = (pallet_length // box_length) * (pallet_width // box_width)
                layers = max_loading_height // box_height
                return int(boxes_per_layer * layers)

            self.boxes1 = calculate_boxes_per_pallet(pallet_length, pallet_width, box1_length, box1_width, box1_height)
            self.additional_boxes_counts = [calculate_boxes_per_pallet(pallet_length, pallet_width, length, width, height) for length, width, height, weight in additional_boxes]

            # Debug print statements to verify box counts
            print(f"Number of Box 1: {self.boxes1}")
            for i, count in enumerate(self.additional_boxes_counts):
                print(f"Number of Box {i + 2}: {count}")

            # Simulate loading time
            QTimer.singleShot(5000, lambda: self.show_result(pallet_length, pallet_width, max_loading_height, box1_length, box1_width, box1_height, additional_boxes, total_weight))
        except ValueError:
            QMessageBox.critical(self, "Error", "Please enter valid numeric values.")
            self.loading_label.hide()
            self.loading_movie.stop()

    def show_result(self, pallet_length, pallet_width, max_loading_height, box1_length, box1_width, box1_height, additional_boxes, total_weight):
        self.loading_label.hide()
        self.loading_movie.stop()

        # Show 3D view
        self.gl_view.show()
        self.gl_view.clear()

        # Add boxes to the 3D view
        for i in range(self.boxes1):
            x = (i % (pallet_length // box1_length)) * box1_length
            y = ((i // (pallet_length // box1_length)) % (pallet_width // box1_width)) * box1_width
            z = (i // ((pallet_length // box1_length) * (pallet_width // box1_width))) * box1_height
            box = create_box_mesh(x, y, z, box1_length, box1_width, box1_height)
            self.gl_view.addItem(box)

        for i, (length, width, height, weight) in enumerate(additional_boxes):
            for j in range(self.additional_boxes_counts[i]):
                x = (j % (pallet_length // length)) * length
                y = ((j // (pallet_length // length)) % (pallet_width // width)) * width
                z = (j // ((pallet_length // length) * (pallet_width // width))) * height
                box = create_box_mesh(x, y, z, length, width, height)
                self.gl_view.addItem(box)

        result_text = f"Box 1: {self.boxes1} boxes"
        for i, count in enumerate(self.additional_boxes_counts):
            result_text += f"\nBox {i + 2}: {count} boxes"
        if self.box_weight_checkbox.isChecked():
            result_text += f"\nTotal Weight: {total_weight} kg"
        self.result_label.setText(result_text)
        self.result_label.show()

        # Calculate the appropriate camera distance
        max_dimension = max(pallet_length, pallet_width, max_loading_height)
        self.gl_view.opts['distance'] = max_dimension * 3

        # Disable user interaction
        self.gl_view.pan(0, 0, 0)
        self.gl_view.orbit(0, 0)
        self.gl_view.setCameraPosition(distance=max_dimension * 3)

    def change_language(self, language):
        self.current_language = language
        self.setWindowTitle(translations[language]["Pallet Calculator"])
        self.form_layout.labelForField(self.pallet_size_input).setText(translations[language]["Pallet Size:"])
        self.form_layout.labelForField(self.box1_length_input).setText(translations[language][f"Box 1 Length ({self.unit_input.currentText().lower()}):"])
        self.form_layout.labelForField(self.box1_width_input).setText(translations[language][f"Box 1 Width ({self.unit_input.currentText().lower()}):"])
        self.form_layout.labelForField(self.box1_height_input).setText(translations[language][f"Box 1 Height ({self.unit_input.currentText().lower()}):"])
        self.form_layout.labelForField(self.max_loading_height_input).setText(translations[language][f"Max Loading Height ({self.unit_input.currentText().lower()}):"])
        self.add_box_button.setText(translations[language]["Add Box"])
        self.remove_box_button.setText(translations[language]["Remove Box"])
        self.calculate_button.setText(translations[language]["Calculate"])
        self.box_weight_checkbox.setText(translations[language]["Box Weight"])
        self.created_by_label.setText(translations[language]["Created by Martijn Steenks"])

        if self.box_weight_checkbox.isChecked():
            self.form_layout.labelForField(self.box1_weight_input).setText(translations[language][f"Box 1 Weight (kg):"])
            for i, weight_input in enumerate(self.box_weight_inputs):
                self.form_layout.labelForField(weight_input).setText(translations[language][f"Box {i + 2} Weight (kg):"])