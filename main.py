import sys
import os
from PyQt6.QtWidgets import QRadioButton, QPushButton, QGroupBox, QHBoxLayout, \
    QSpinBox, QLabel, QButtonGroup, QApplication, QVBoxLayout, QWidget, QDoubleSpinBox
from PyQt6 import QtGui
import simulation as sim
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create a matplotlib figure and canvas
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.mutation = False
        self.limit_pop = False
        self.food_search = False
        self.kin_selection = False
        self.parameters = {}
        self.initUI()

    def change_mutation(self):
        if self.mutation:
            self.mutation = False
        else:
            self.mutation = True

    def change_limit_pop(self):
        if self.limit_pop:
            self.limit_pop = False
        else:
            self.limit_pop = True

    def change_food_search(self):
        if self.food_search:
            self.food_search = False
        else:
            self.food_search = True

    def change_kin(self):
        if self.kin_selection:
            self.kin_selection = False
        else:
            self.kin_selection = True

    def launch_sim(self):
        self.parameters["V"] = self.food.value()
        self.parameters["C"] = self.fight.value()
        self.parameters["INITIAL_POP"] = self.pop_ini.value()
        self.parameters["MAX_POP"] = self.pop_max.value()
        self.parameters["INITIAL_DOVE"] = self.pop_dove.value() / 100
        self.parameters["GEN"] = self.length_sim.value()

        if self.seed.value() < 0:
            self.parameters["SEED"] = -1
        else:
            self.parameters["SEED"] = self.seed.value()

        if self.mutation:
            self.parameters["DOVE_MUTATION"] = self.dove_to_hawk.value() / 100
            self.parameters["HAWK_MUTATION"] = self.hawk_to_dove.value() / 100
        else:
            self.parameters["DOVE_MUTATION"] = 0
            self.parameters["HAWK_MUTATION"] = 0

        if self.limit_pop:
            self.parameters["LIMIT_RANDOM"] = self.pop_limit_random_check.isChecked()
            self.parameters["LIMIT_OLD"] = self.pop_limit_olders_win.isChecked()
            self.parameters["LIMIT_YOUNG"] = self.pop_limit_youngers_win.isChecked()
        else:
            self.parameters["LIMIT_RANDOM"] = True
            self.parameters["LIMIT_OLD"] = False
            self.parameters["LIMIT_YOUNG"] = False

        if self.food_search:
            self.parameters["IS_FOOD_SEARCH"] = True
            self.parameters["HAWK_MEAN"] = self.mean_hawk.value()
            self.parameters["HAWK_SHAPE"] = self.std_hawk.value()
            self.parameters["DOVE_MEAN"] = self.mean_dove.value()
            self.parameters["DOVE_SHAPE"] = self.std_dove.value()
        else:
            self.parameters["IS_FOOD_SEARCH"] = False
        print(self.parameters)

        if self.kin_selection:
            self.parameters["IS_KIN_SELECT"] = True
        else:
            self.parameters["IS_KIN_SELECT"] = False

        new_fig = sim.run_sim(self.parameters)
        new_canvas = FigureCanvas(new_fig)
        self.fig_box.removeWidget(self.image)
        self.fig_box.replaceWidget(self.canvas, new_canvas)
        self.canvas = new_canvas
        self.fig = new_fig
        self.canvas.draw()

    def update_groupbox_graph(self):
        self.groupbox_graph.update()
    def default(self):
        pass

    def update_fight_range(self, food_value):
        self.fight.setRange((food_value / 2) + 0.1, 50)

    def initUI(self):
        # Get screen dimensions
        screen = QtGui.QGuiApplication.primaryScreen()
        screen_geo = screen.availableGeometry()
        screen_width = screen_geo.width()
        screen_height = screen_geo.height()
        # Create checkboxes
        self.food = QDoubleSpinBox(self)
        self.food.setValue(10.0)
        self.food.setRange(0, 50)
        self.food.valueChanged.connect(self.update_fight_range)

        self.fight = QDoubleSpinBox(self)
        self.fight.setValue(5.1)
        self.update_fight_range(self.food.value())

        self.pop_ini = QSpinBox(self)
        self.pop_ini.setRange(0, 10000)
        self.pop_ini.setValue(100)

        self.pop_max = QSpinBox(self)
        self.pop_max.setRange(0, 10000)
        self.pop_max.setValue(1000)

        self.pop_dove = QSpinBox(self)
        self.pop_dove.setRange(0, 100)
        self.pop_dove.setValue(50)

        ## length of simulation
        self.length_sim = QSpinBox(self)
        self.length_sim.setRange(0, 10000)
        self.length_sim.setValue(100)

        ## limitation of population
        self.pop_limit_random_check = QRadioButton('Random', self)
        self.pop_limit_random_check.setChecked(True)
        self.pop_limit_olders_win = QRadioButton('Olders win', self)
        self.pop_limit_youngers_win = QRadioButton('Youngers win', self)

        self.launch = QPushButton("Apply & Launch")
        self.launch.clicked.connect(self.launch_sim)


        self.seed = QSpinBox(self)
        self.seed.setMinimum(-1)
        self.seed.setMaximum(10000)
        self.seed.setValue(1)
        seed_label = QLabel('Seed: ')

        ## mutation
        self.dove_to_hawk = QSpinBox(self)
        self.hawk_to_dove = QSpinBox(self)
        dove_to_hawk_label = QLabel('Percentage dove to hawk mutation: ')
        hawk_to_dove_label = QLabel('Percentage hawk to dove mutation: ')
        self.dove_to_hawk.setValue(10)
        self.hawk_to_dove.setValue(10)
        self.dove_to_hawk.setRange(0, 100)
        self.hawk_to_dove.setRange(0, 100)

        ## Food search
        self.mean_dove = QSpinBox(self)
        self.mean_hawk = QSpinBox(self)
        self.std_dove = QSpinBox(self)
        self.std_hawk = QSpinBox(self)
        self.std_dove.setMinimum(0)
        self.std_hawk.setMinimum(0)
        food_label_dove = QLabel('Dove')
        food_label_hawk = QLabel('Hawk')
        food_label_mean_h = QLabel('Mean')
        food_label_mean_d = QLabel('Mean')
        food_label_std_h = QLabel('Std')
        food_label_std_d = QLabel('Std')

        V = QLabel('Food Value:')
        C = QLabel('Fight Cost:')
        N = QLabel('Initial Population:')
        M = QLabel('Maximum Population:')
        D = QLabel('Initial Dove Fraction:')
        G = QLabel('Simulation Length:')

        ## kin selection
        kin_select_label = QLabel('Work in progress')

        #test graph
        # Create a QVBoxLayout and add the FigureCanvasQTAgg widget to it
        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)

        # Get the absolute path to the directory containing the script
        dir_path = os.path.dirname(os.path.abspath(__file__))

        # Get the absolute path to the 'welcome.jpg' file in the same directory
        file_path = os.path.join(dir_path, 'welcome.jpg')

        # Load the image using QPixmap
        self.image = QLabel()
        self.pixmap = QtGui.QPixmap(file_path)
        max_height = int(screen_height * 0.8)
        self.pixmap = self.pixmap.scaledToHeight(max_height)
        self.image.setPixmap(self.pixmap)
        self.image.setScaledContents(True)


        self.fig_box = QVBoxLayout()
        self.fig_box.addWidget(self.image)
        self.fig_box.addWidget(self.canvas)

        ## elon musk
        lunch_box = QVBoxLayout()
        lunch_box.addWidget(self.launch)

        # Create layouts
        hbox1 = QVBoxLayout()
        hbox1.addWidget(V)
        hbox1.addWidget(self.food)
        hbox1.addWidget(C)
        hbox1.addWidget(self.fight)
        hbox1.addWidget(N)
        hbox1.addWidget(self.pop_ini)
        hbox1.addWidget(M)
        hbox1.addWidget(self.pop_max)
        hbox1.addWidget(D)
        hbox1.addWidget(self.pop_dove)
        hbox1.addWidget(G)
        hbox1.addWidget(self.length_sim)
        hbox1.addWidget(seed_label)
        hbox1.addWidget(self.seed)

        ## Limitation of population
        limit_pop_group = QButtonGroup()
        limit_pop_group.addButton(self.pop_limit_random_check)
        limit_pop_group.addButton(self.pop_limit_olders_win)
        limit_pop_group.addButton(self.pop_limit_youngers_win)
        limit_pop_group.setExclusive(True)
        #
        box_limit_pop = QHBoxLayout()
        box_limit_pop.addWidget(self.pop_limit_random_check)
        box_limit_pop.addWidget(self.pop_limit_olders_win)
        box_limit_pop.addWidget(self.pop_limit_youngers_win)

        # mutation
        hawk_to_dove_box = QHBoxLayout()
        hawk_to_dove_box.addWidget(hawk_to_dove_label)
        hawk_to_dove_box.addWidget(self.hawk_to_dove)

        dove_to_hawk_box = QHBoxLayout()
        dove_to_hawk_box.addWidget(dove_to_hawk_label)
        dove_to_hawk_box.addWidget(self.dove_to_hawk)

        mutation_box = QVBoxLayout()
        mutation_box.addLayout(hawk_to_dove_box)
        mutation_box.addLayout(dove_to_hawk_box)

        # food_search
        food_search_dove_box = QHBoxLayout()
        food_search_dove_box.addWidget(food_label_dove)
        food_search_dove_box.addWidget(food_label_mean_d)
        food_search_dove_box.addWidget(self.mean_dove)
        food_search_dove_box.addWidget(food_label_std_d)
        food_search_dove_box.addWidget(self.std_dove)

        food_search_hawk_box = QHBoxLayout()
        food_search_hawk_box.addWidget(food_label_hawk)
        food_search_hawk_box.addWidget(food_label_mean_h)
        food_search_hawk_box.addWidget(self.mean_hawk)
        food_search_hawk_box.addWidget(food_label_std_h)
        food_search_hawk_box.addWidget(self.std_hawk)

        food_search_box = QVBoxLayout()
        food_search_box.addLayout(food_search_dove_box)
        food_search_box.addLayout(food_search_hawk_box)

        kin_selection_box = QVBoxLayout()
        kin_selection_box.addWidget(kin_select_label)

        # Create group boxes
        groupbox1 = QGroupBox('General settings', self)
        groupbox1.setStyleSheet('QGroupBox{border: 2px solid black;}')
        groupbox1.setContentsMargins(10, 10, 10, 10)
        groupbox1.setLayout(hbox1)

        groupbox_limit_pop = QGroupBox('Limitation of population', self)
        groupbox_limit_pop.setCheckable(True)
        groupbox_limit_pop.setChecked(self.limit_pop)
        groupbox_limit_pop.setStyleSheet('QGroupBox{border: 2px solid black;}')
        groupbox_limit_pop.setLayout(box_limit_pop)
        groupbox_limit_pop.clicked.connect(self.change_limit_pop)

        groupbox_mutation = QGroupBox('Mutation', self)
        groupbox_mutation.setCheckable(True)
        groupbox_mutation.setChecked(self.mutation)
        groupbox_mutation.setStyleSheet('QGroupBox{border: 2px solid black;}')
        groupbox_mutation.setLayout(mutation_box)
        groupbox_mutation.clicked.connect(self.change_mutation)

        groupbox_food_search = QGroupBox('Time to catch', self)
        groupbox_food_search.setCheckable(True)
        groupbox_food_search.setChecked(self.food_search)
        groupbox_food_search.setStyleSheet('QGroupBox{border: 2px solid black;}')
        groupbox_food_search.setLayout(food_search_box)
        groupbox_food_search.clicked.connect(self.change_food_search)

        groupbox_kin = QGroupBox('Kin Selection', self)
        groupbox_kin.setCheckable(True)
        groupbox_kin.setChecked(self.kin_selection)
        groupbox_kin.setStyleSheet('QGroupBox{border: 2px solid black;}')
        groupbox_kin.setLayout(kin_selection_box)
        groupbox_kin.clicked.connect(self.change_kin)

        groupbox_lunch_box = QGroupBox('Launch', self)
        groupbox_lunch_box.setStyleSheet('QGroupBox{border: 2px solid black;}')

        groupbox_lunch_box.setLayout(lunch_box)

        vbox = QVBoxLayout()
        vbox.addWidget(groupbox1)
        vbox.addWidget(groupbox_limit_pop)
        vbox.addWidget(groupbox_mutation)
        vbox.addWidget(groupbox_food_search)
        vbox.addWidget(groupbox_kin)
        vbox.addWidget(groupbox_lunch_box)

        groupbox_parameters = QGroupBox('Parameters', self)
        groupbox_parameters.setStyleSheet('QGroupBox{border: 2px solid black;}')
        groupbox_parameters.setContentsMargins(10, 10, 10, 10)
        groupbox_parameters.setLayout(vbox)

        self.groupbox_graph = QGroupBox('Graph', self)
        self.groupbox_graph.setStyleSheet('QGroupBox{border: 2px solid black;}')
        self.groupbox_graph.setContentsMargins(10, 10, 10, 10)
        self.groupbox_graph.setLayout(self.fig_box)


        main_layout = QHBoxLayout()
        main_layout.addWidget(groupbox_parameters)
        main_layout.addWidget(self.groupbox_graph)


        # Set the main layout
        self.setLayout(main_layout)
        # Set default window size as a ratio of the screen size
        # Set window size to 80% of screen size
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        self.setGeometry(0, 0, window_width, window_height)
        self.setWindowTitle('Hawk and Dove GUI by Lu and Flo')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()

    sys.exit(app.exec())

