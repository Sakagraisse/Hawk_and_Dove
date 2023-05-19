import sys
import os
from PyQt6.QtWidgets import QRadioButton, QPushButton, QGroupBox, QHBoxLayout, \
    QSpinBox, QLabel, QButtonGroup, QApplication, QVBoxLayout, QWidget, QDoubleSpinBox, QProgressBar, \
    QGridLayout
from PyQt6.QtCore import QThread , pyqtSignal
from PyQt6 import QtGui
import simulation as sim
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
import time
import pandas as pd
from matplotlib.figure import Figure


class handle_simulation(QThread):
    simulation = pyqtSignal(Figure)
    def __init__(self, parameters, results):
        super().__init__()
        self.parameters = parameters
        self.results = results
    def run(self):
        new_fig = sim.run_sim(self.parameters,self.results)
        self.simulation.emit(new_fig)

class update_progress_bar(QThread):
    progress = pyqtSignal(int)
    def __init__(self, results, parameters):
        super().__init__()
        self.parameters = parameters
        self.results = results
    def run(self):
        #check every 100ms the number of line or results and update the progress bar
        while len(self.results) < self.parameters["GEN"]:
            time.sleep(0.1)
            percent = int(len(self.results) / self.parameters["GEN"] * 100)
            self.progress.emit(percent)





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
        self.prog_bar.setValue(0)
        self.results = pd.DataFrame(columns=["generation", "total population",
                                        "population increase %",
                                        "proportion of dove", "proportion of hawk", "avg life expectancy"])
        self.parameters["PHH"] = self.p_HH.value()
        self.parameters["PHD"] = self.p_HD.value()
        self.parameters["PDH"] = self.p_DH.value()
        self.parameters["PDD"] = self.p_DD.value()
        self.parameters["V_DEF"] = self.v_default.value()
        self.parameters["NODES"] = self.nodes.value()
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
        #(self.parameters)

        if self.kin_selection:
            self.parameters["IS_KIN_SELECT"] = True
        else:
            self.parameters["IS_KIN_SELECT"] = False


        self.thread = handle_simulation(self.parameters,self.results)
        self.th2 = update_progress_bar(self.results, self.parameters)

        self.thread.start()
        self.th2.start()

        self.th2.progress.connect(self.update_babar)
        self.thread.simulation.connect(self.handle_simulation_result)

        self.prog_bar.setValue(100)
        self.prog_bar.update()

    def stop_threads(self):
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.stop()
            self.thread.quit()
            self.thread.terminate()
            self.thread.wait()

        if hasattr(self, 'th2') and self.th2.isRunning():
            self.th2.stop()
            self.th2.quit()
            self.th2.terminate()
            self.th2.wait()
        self.handle_simulation_result(None)
        self.update_babar(0)
    def update_babar(self, percent):
        self.prog_bar.setValue(percent)
        self.prog_bar.update()


    def handle_simulation_result(self, new_fig):
        self.fig = new_fig

        new_canvas = FigureCanvas(self.fig)
        self.fig_box.removeWidget(self.image)
        self.fig_box.replaceWidget(self.canvas, new_canvas)
        self.canvas = new_canvas
        self.switch_graph.setChecked(True)

    def update_groupbox_graph(self):
        self.groupbox_graph.update()

    def update_fight_range(self, food_value):
        self.fight.setRange((food_value / 2) + 0.1, 1000)

    def change_to_graph(self):
            self.image.hide()
            self.canvas.show()


    def change_to_default(self):
        self.image.show()
        self.canvas.hide()

    ################
    # creating the UI main definition and layout
    ################


    def initUI(self):
        # Get screen dimensions
        screen = QtGui.QGuiApplication.primaryScreen()
        screen_geo = screen.availableGeometry()
        screen_width = screen_geo.width()
        screen_height = screen_geo.height()

        #create progress bar
        self.prog_bar = QProgressBar(self)

        #create the matrix of parameters
        matrix_v_grid = QGridLayout()
        self.p_HH = QDoubleSpinBox(self)
        self.p_HH.setValue(-1)
        self.p_HH.setRange(-50,100)
        matrix_v_grid.addWidget(self.p_HH,1,1)
        self.p_HD = QDoubleSpinBox(self)
        self.p_HD.setValue(2)
        self.p_HD.setRange(-50,100)
        matrix_v_grid.addWidget(self.p_HD,1,2)
        self.p_DH = QDoubleSpinBox(self)
        self.p_DH.setValue(0)
        self.p_DH.setRange(-50,100)
        matrix_v_grid.addWidget(self.p_DH,2,1)
        self.p_DD = QDoubleSpinBox(self)
        self.p_DD.setValue(1)
        self.p_DD.setRange(-50,100)
        matrix_v_grid.addWidget(self.p_DD,2,2)
        matrix_v_grid.addWidget(QLabel("Payoff Matrix"), 0,0)
        matrix_v_grid.addWidget(QLabel("Hawk"),0,1)
        matrix_v_grid.addWidget(QLabel("Hawk"),1,0)
        matrix_v_grid.addWidget(QLabel("Dove"),0,2)
        matrix_v_grid.addWidget(QLabel("Dove"),2,0)
        self.v_default = QDoubleSpinBox(self)
        self.v_default.setValue(self.p_HD.value())
        v_def = QLabel("Default Food Value")

        #create the bix for entering the initial population
        self.pop_ini = QSpinBox(self)
        self.pop_ini.setRange(0, 10000)
        self.pop_ini.setValue(100)

        #create the box for entering the maximum population
        self.pop_max = QSpinBox(self)
        self.pop_max.setRange(0, 10_000)
        self.pop_max.setValue(1_000)

        #create the box for entering the number of nodes ( = number of food sources)
        self.nodes = QSpinBox(self)
        self.nodes.setRange(0,10_000)
        self.nodes.setValue(self.pop_max.value())

        #create the box for entering the initial proportion of doves
        self.pop_dove = QSpinBox(self)
        self.pop_dove.setRange(0, 100)
        self.pop_dove.setValue(50)

        #length of simulation
        self.length_sim = QSpinBox(self)
        self.length_sim.setRange(0, 10_000)
        self.length_sim.setValue(100)

        #greating the buttons to choose the method to remove players above the limit
        self.pop_limit_random_check = QRadioButton('Random', self)
        self.pop_limit_random_check.setChecked(True)
        self.pop_limit_olders_win = QRadioButton('Olders win', self)
        self.pop_limit_youngers_win = QRadioButton('Youngers win', self)

        #creating the button to start and stop the simulation
        self.launch = QPushButton("Apply and start")
        self.launch.setStyleSheet("background-color: green;")
        self.launch.clicked.connect(self.launch_sim)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("background-color: red;")
        self.stop_button.clicked.connect(self.stop_threads)

        #creating box to choice the random seed manually if needed ( for debugging )
        self.seed = QSpinBox(self)
        self.seed.setMinimum(-1)
        self.seed.setMaximum(10000)
        self.seed.setValue(1)
        seed_label = QLabel('Seed (enter negative value for random): ')

        #creating the sliders to choose the mutation rate
        self.dove_to_hawk = QSpinBox(self)
        self.hawk_to_dove = QSpinBox(self)
        dove_to_hawk_label = QLabel('Percentage dove to hawk mutation: ')
        hawk_to_dove_label = QLabel('Percentage hawk to dove mutation: ')
        self.dove_to_hawk.setValue(10)
        self.hawk_to_dove.setValue(10)
        self.dove_to_hawk.setRange(0, 100)
        self.hawk_to_dove.setRange(0, 100)

        #creating the boxes to choose mean and std of the food search value
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

        #creating the needed labels
        NODES = QLabel("Number of food nodes")
        N = QLabel('Initial Population:')
        M = QLabel('Maximum Population:')
        D = QLabel('Initial Dove Fraction:')
        G = QLabel('Simulation Length:')


        # creating the buttons to switch between the graph and the instructions
        self.switch_graph = QRadioButton("Graph",self)
        self.switch_default = QRadioButton("Instructions",self)
        self.switch_default.setChecked(True)
        switch_group = QButtonGroup()
        switch_group.addButton(self.switch_graph)
        switch_group.addButton(self.switch_default)
        switch_group.setExclusive(True)

        self.switch_graph.clicked.connect(self.change_to_graph)
        self.switch_default.clicked.connect(self.change_to_default)

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
        lunch_box.addWidget(self.stop_button)

        ################
        # creating layouts for the left side ( all the settings )
        ################
        general_setting_layout = QVBoxLayout()
        general_setting_layout.addLayout(matrix_v_grid)
        general_setting_layout.addWidget(v_def)
        general_setting_layout.addWidget(self.v_default)
        general_setting_layout.addWidget(N)
        general_setting_layout.addWidget(self.pop_ini)
        general_setting_layout.addWidget(M)
        general_setting_layout.addWidget(self.pop_max)
        general_setting_layout.addWidget(NODES)
        general_setting_layout.addWidget(self.nodes)
        general_setting_layout.addWidget(D)
        general_setting_layout.addWidget(self.pop_dove)
        general_setting_layout.addWidget(G)
        general_setting_layout.addWidget(self.length_sim)
        general_setting_layout.addWidget(seed_label)
        general_setting_layout.addWidget(self.seed)

        ## Limitation of population
        limit_pop_button_Qgroup = QButtonGroup()
        limit_pop_button_Qgroup.addButton(self.pop_limit_random_check)
        limit_pop_button_Qgroup.addButton(self.pop_limit_olders_win)
        limit_pop_button_Qgroup.addButton(self.pop_limit_youngers_win)
        limit_pop_button_Qgroup.setExclusive(True)
        #
        pop_limit_layout = QHBoxLayout()
        pop_limit_layout.addWidget(self.pop_limit_random_check)
        pop_limit_layout.addWidget(self.pop_limit_olders_win)
        pop_limit_layout.addWidget(self.pop_limit_youngers_win)

        # mutation
        hawk_to_dove_layout = QHBoxLayout()
        hawk_to_dove_layout.addWidget(hawk_to_dove_label)
        hawk_to_dove_layout.addWidget(self.hawk_to_dove)

        dove_to_hawk_layout = QHBoxLayout()
        dove_to_hawk_layout.addWidget(dove_to_hawk_label)
        dove_to_hawk_layout.addWidget(self.dove_to_hawk)

        mutation_layout = QVBoxLayout()
        mutation_layout.addLayout(hawk_to_dove_layout)
        mutation_layout.addLayout(dove_to_hawk_layout)

        # food_search
        time_catch_dove_layout = QHBoxLayout()
        time_catch_dove_layout.addWidget(food_label_dove)
        time_catch_dove_layout.addWidget(food_label_mean_d)
        time_catch_dove_layout.addWidget(self.mean_dove)
        time_catch_dove_layout.addWidget(food_label_std_d)
        time_catch_dove_layout.addWidget(self.std_dove)

        time_catch_hawk_layout = QHBoxLayout()
        time_catch_hawk_layout.addWidget(food_label_hawk)
        time_catch_hawk_layout.addWidget(food_label_mean_h)
        time_catch_hawk_layout.addWidget(self.mean_hawk)
        time_catch_hawk_layout.addWidget(food_label_std_h)
        time_catch_hawk_layout.addWidget(self.std_hawk)

        food_search_layout = QVBoxLayout()
        food_search_layout.addLayout(time_catch_dove_layout)
        food_search_layout.addLayout(time_catch_hawk_layout)


        ################
        # creating the group boxes for the left side ( all the settings )
        ################

        parameters_box = QGroupBox('General settings', self)
        parameters_box.setStyleSheet('QGroupBox{border: 2px solid black;}')
        parameters_box.setContentsMargins(10, 10, 10, 10)
        parameters_box.setLayout(general_setting_layout)

        limit_pop_box = QGroupBox('Limitation of population', self)
        limit_pop_box.setCheckable(True)
        limit_pop_box.setChecked(self.limit_pop)
        limit_pop_box.setStyleSheet('QGroupBox{border: 2px solid black;}')
        limit_pop_box.setLayout(pop_limit_layout)
        limit_pop_box.clicked.connect(self.change_limit_pop)

        mutation_box = QGroupBox('Mutation', self)
        mutation_box.setCheckable(True)
        mutation_box.setChecked(self.mutation)
        mutation_box.setStyleSheet('QGroupBox{border: 2px solid black;}')
        mutation_box.setLayout(mutation_layout)
        mutation_box.clicked.connect(self.change_mutation)

        food_search_box = QGroupBox('Time to catch', self)
        food_search_box.setCheckable(True)
        food_search_box.setChecked(self.food_search)
        food_search_box.setStyleSheet('QGroupBox{border: 2px solid black;}')
        food_search_box.setLayout(food_search_layout)
        food_search_box.clicked.connect(self.change_food_search)


        starting_box = QGroupBox('Launch', self)
        starting_box.setStyleSheet('QGroupBox{border: 2px solid black;}')
        starting_box.setLayout(lunch_box)

        left_box = QVBoxLayout()
        left_box.addWidget(parameters_box)
        left_box.addWidget(limit_pop_box)
        left_box.addWidget(mutation_box)
        left_box.addWidget(food_search_box)
        left_box.addWidget(starting_box)

        groupbox_parameters = QGroupBox('Parameters', self)
        groupbox_parameters.setStyleSheet('QGroupBox{border: 2px solid black;}')
        groupbox_parameters.setContentsMargins(10, 10, 10, 10)
        groupbox_parameters.setLayout(left_box)

        ################
        # creating the layouts and the group boxes for the left side ( viewing the graph
        ################

        choice_graph = QHBoxLayout()
        choice_graph.addWidget(self.switch_default)
        choice_graph.addWidget(self.switch_graph)



        display_box = QGroupBox('Graph', self)
        display_box.setStyleSheet('QGroupBox{border: 2px solid black;}')
        display_box.setContentsMargins(10, 10, 10, 10)
        display_box.setLayout(self.fig_box)

        right_side = QVBoxLayout()
        right_side.addWidget(self.prog_bar)
        right_side.addLayout(choice_graph)
        right_side.addWidget(display_box)

       #Setup main windows

        main_layout = QHBoxLayout()
        main_layout.addWidget(groupbox_parameters)
        main_layout.addLayout(right_side)


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
