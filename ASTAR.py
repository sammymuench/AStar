import sys
import time
import numpy as np
import copy
from stateSpace import state
from bucketQueue import bucket

class AStar:
    def __init__(self):
        self.runtime = 0
        self.nodes_explored = 0
        self.path_length = 0
        self.energy_spent = 0
        self.open_nodes = bucket()
        self.closed_nodes = 0
        self.lot_map = None
        self.parking_spot = (-1, -1)
        self.chosen_heuristic = None
        self.tot_num_patients = 0

    def process_map(self, raw_map):
        '''
        Input: 
        Processes map, which should be strings
        '''
        assert isinstance(raw_map, str)
        raw_map = raw_map.split('\n')
        processed_map = []
        for row in raw_map:
            curr_row = row.split(';')
            processed_map.append(curr_row)
        
        for i, row in enumerate(processed_map):
            for j, spot_type in enumerate(row):
                if spot_type == 'P':
                    self.parking_spot = (i, j)
        return np.array(processed_map)

    def read_map(self, argv):
        '''
        Input: self and command line arguments (includes map file name):
        Output: None

        Sets lot_map to string given command line arguments
        '''
        #check if command line is valid
        if len(argv) != 3:
            print('Usage: python ASTARTraslados.py <map.csv file to read> <num-h>')
            sys.exit(1)
        sh_file_name = argv[1]
                
        if sh_file_name[-3:] != 'csv':
            print(sh_file_name)
            print(f'Error: {sh_file_name[-2]}file must be .csv file')
            sys.exit(1)
        
        self.chosen_heuristic = argv[2]
        
        #opens file
        try:
            with open(sh_file_name, 'r') as file:
                #takes unprocessed string and returns map as array
                self.lot_map = self.process_map(file.read())
                return self.lot_map
        except FileNotFoundError:
            print(f'Error: file {sh_file_name} not found')
            sys.exit(1)
        except Exception as e:
            print(f'Error occurred: {str(e)}')
            sys.exit(1)

    def get_init_patient_locations(self):
        '''
        Input: self
        Output: Array of all locations of patients
        '''
        
        C_locations = self.lot_map == 'C'
        N_locations = self.lot_map == 'N'
        patients_indices_C = np.where(C_locations)
        patients_indices_N = np.where(N_locations)
        patients_C = list(zip(patients_indices_C[0], patients_indices_C[1]))
        patients_N = list(zip(patients_indices_N[0], patients_indices_N[1]))
        return patients_C, patients_N

    def get_hospital_locations(self):
        '''
        Input: self, lot_map specifically
        Output: tuple (indices of hospital locations contagious, indices of hospital)
        '''
        CC_locations = self.lot_map == 'CC'
        CN_locations = self.lot_map == 'CN'
        indices_CC = np.where(CC_locations)
        indices_CN = np.where(CN_locations)
        locs_CC = list(zip(indices_CC[0], indices_CC[1]))
        locs_CN = list(zip(indices_CN[0], indices_CN[1]))
        self.CC_locs = locs_CC
        self.CN_locs = locs_CN

    def state_is_goal(self, curr_state):
        '''
        Input: current state
        Output: whether the state is a goal
        '''
        return curr_state.curr_spot == self.parking_spot and len(curr_state.patient_locations_C + curr_state.patient_locations_N) == 0 and self.tot_num_patients == curr_state.patients_dropped_off

    def reconstruct_path(self, curr_state):
        '''
        Reconstructs goal path
        '''
        print(curr_state.patient_locations_C, curr_state.patient_locations_N)
        path = []
        while curr_state:
            path.insert(0, curr_state)
            if curr_state and curr_state.parent:
                if curr_state.parent.curr_spot == (1, 2):
                    print('Heuristic', curr_state.curr_spot, curr_state.heuristic_two(self.CC_locs, self.CN_locs, self.parking_spot))
            curr_state = curr_state.parent
        return path

    def run(self):
        patient_locations_C, patient_locations_N = algorithm.get_init_patient_locations()
        init_num_patients = len(patient_locations_C)
        algorithm.get_hospital_locations()
        self.tot_num_patients = len(patient_locations_C + patient_locations_N)
        state_one = state(patient_locations_C=patient_locations_C, patient_locations_N=patient_locations_N)
        state_one.set_initial_spot(algorithm.lot_map)

        #open set is a bucket queue, closed set is a dict
        open = bucket()
        closed = {}
        start_node = state(patient_locations_C=patient_locations_C, patient_locations_N=patient_locations_N)
        start_node.set_initial_spot(self.lot_map)

        open.addAt(start_node, 0)
        i=0
        while not open.isEmpty(): 
            i+=1 
            curr = open.popFront()
            #print('curr', curr)
            #check if current node is goal
            if self.state_is_goal(curr):
                return self.reconstruct_path(curr), i

            for child_state in curr.generate_successors(self.lot_map):
                if curr.__str__() == "{'Current spot': (1, 2), 'Contagious Patients Holding': 0, 'Non Contagious Patients Holding': 6, 'Patient Locations N': [(0, 1)], 'Patient Locations C': [(0, 0), (0, 2), (0, 9), (4, 7), (6, 4)]}":
                    print('Heuristic for shitty one', child_state.curr_spot, child_state.heuristic_two(self.CC_locs, self.CN_locs, self.parking_spot, True))
                #print('current child',child_state, 'with num patients',(len(child_state.patient_locations_N)))
                try:
                    x = closed[curr.hash_func()]
                except KeyError:
                    g_val = child_state.energy_used
                    h_val = child_state.heuristic(self.chosen_heuristic, self.CC_locs, self.CN_locs, self.parking_spot, init_num_patients)
                    f_val = g_val + h_val
                    open.addAt(child_state, f_val)

            closed[curr.hash_func()] = curr
            if i % 10000 == 0: print(curr, 'f =', curr.energy_used + curr.heuristic(self.chosen_heuristic, self.CC_locs, self.CN_locs, self.parking_spot, init_num_patients))
            

if __name__ == '__main__':

    algorithm = AStar()
    processed_map = algorithm.read_map(sys.argv)
    start_time = time.time()
    path, expanded_nodes = algorithm.run()
    end_time = time.time()
    elapsed_time = end_time - start_time #run the algorithm

    path_file = open(f'{sys.argv[1][0:-4]}-{sys.argv[2]}.output', 'w')
    for node in path:
        print(node)
        path_file.write(f'{node.curr_spot}:{processed_map[node.curr_spot]}:{node.energy_left}')
        if path.index(node) != -1: path_file.write('\n') #write the outputted path
    
    info_file = open(f'{sys.argv[1][0:-4]}-{sys.argv[2]}.stat', 'w')
    info_file.write(f'Total time: {elapsed_time}\n')
    info_file.write(f'Total cost: {path[-1].energy_used}\n')
    info_file.write(f'Plan length: {len(path)}\n')
    info_file.write(f'Expanded nodes: {expanded_nodes}')

    path_file.close()
    info_file.close() #write to information files


