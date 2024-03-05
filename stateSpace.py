import sys
import time
import numpy as np
import copy

'''
Implementation of state space
'''

class state:

    def __init__(self, patient_locations_C = [], patient_locations_N = [], curr_spot = (-1, -1), energy_left = 50, energy_used = 0, holding_C = 0, holding_N = 0, patients_dropped_off = 0, parent = None, parking_spot = None):
        '''
        Initialize state space, which is represented by:
        spot tuple:(row, col), energy left , energy used, #contagious in truck, #non contagious in truck, #patients dropped off, array of patient locations no picked up yet
        '''
        self.curr_spot = curr_spot
        self.energy_left = energy_left
        self.energy_used = energy_used
        self.holding_C = holding_C
        self.holding_N = holding_N
        self.patients_dropped_off = patients_dropped_off
        self.patient_locations_C = patient_locations_C
        self.patient_locations_N = patient_locations_N
        self.parking_spot = parking_spot
        self.parent = parent

    def move_no_action(self, row, col, spot_id):
        '''
        Facilitates moving from one spot to another without doing any action other than loss of energy (like if we move to C and cannot pick them up, or CN and cannot drop off).
        Also facilitates moving to parking and recharging energy. 
        '''
        try:
            if spot_id == 'P':
                #recharge parking
                return state(parking_spot=self.parking_spot, parent=self, curr_spot = (row, col), energy_left=50, energy_used=self.energy_used + 1, holding_C=self.holding_C, holding_N=self.holding_N, patient_locations_C=self.patient_locations_C, patient_locations_N= self.patient_locations_N, patients_dropped_off=self.patients_dropped_off)
        
            if int(spot_id) == 1 or int(spot_id) == 2:
                #if regular spot
                return state(parking_spot=self.parking_spot, parent=self, curr_spot = (row, col), energy_left=self.energy_left - int(spot_id), energy_used=self.energy_used + int(spot_id), holding_C=self.holding_C, holding_N=self.holding_N, patient_locations_C=self.patient_locations_C, patient_locations_N= self.patient_locations_N, patients_dropped_off=self.patients_dropped_off)
        except ValueError:
            #if spot is CN or CC or C or N and we cannot do anything
            return state(parking_spot=self.parking_spot, parent=self, curr_spot = (row, col), energy_left=self.energy_left - 1, energy_used=self.energy_used + 1, holding_C=self.holding_C, holding_N=self.holding_N, patient_locations_C=self.patient_locations_C, patient_locations_N= self.patient_locations_N, patients_dropped_off=self.patients_dropped_off)            

        #should never get here
        return state(parking_spot=self.parking_spot, parent=self, curr_spot = (row, col), energy_left=self.energy_left - 1, energy_used=self.energy_used + 1, holding_C=self.holding_C, holding_N=self.holding_N, patient_locations_C=self.patient_locations_C, patient_locations_N= self.patient_locations_N, patients_dropped_off=self.patients_dropped_off)            

    def set_initial_spot(self, lot_map):
        for i, row in enumerate(lot_map):
            for j, spot_type in enumerate(row):
                if spot_type == 'P':
                    self.parking_spot = (i, j)
                    self.curr_spot = (i, j)
                    break
    
    def __str__(self):
        '''
        for use for the hash function for the closed list. Must check if nodes have been visited
        '''

        return str({
            'Current spot': self.curr_spot,
            'Energy Left': self.energy_left,
            'Contagious Patients Holding': self.holding_C,
            'Non Contagious Patients Holding': self.holding_N,
            'Patient Locations N': self.patient_locations_N,
            'Patient Locations C': self.patient_locations_C,
            #'Parent': self.parent
        })
    
    def hash_func(self):
        return hash(self.__str__())
    
    def decide_state(self, row, col, spot_id):

        '''
        Given the current state and spot ID (1,2,C,N,etc), decides what action to take
        '''
        if self.manhattan_distance((row, col), self.parking_spot) > self.energy_left:
            return None
        elif self.energy_left > 1:
            if spot_id == 'CN':
                if self.holding_C == 0:
                    #drop off non-contagious patients if no contagious in the car
                    return state(parking_spot=self.parking_spot, parent=self, curr_spot = (row, col), energy_left=self.energy_left - 1, energy_used=self.energy_used + 1, holding_C=self.holding_C, holding_N=0, patients_dropped_off=self.patients_dropped_off + self.holding_N, patient_locations_C=self.patient_locations_C, patient_locations_N= self.patient_locations_N)
                
                #stay the same as before but just move to CN
                return self.move_no_action(row, col, spot_id)                    
            elif spot_id == 'CC':
                #drop off all contagious patients
                return state(parking_spot=self.parking_spot, parent=self, curr_spot = (row, col), energy_left=self.energy_left - 1, energy_used= self.energy_used + 1, holding_C=0, holding_N=self.holding_N, patients_dropped_off=self.patients_dropped_off + self.holding_C, patient_locations_C=self.patient_locations_C, patient_locations_N= self.patient_locations_N)
            elif spot_id == 'C':
                if self.holding_C < 2 and self.holding_N <= 8 and (row, col) in self.patient_locations_C:
                    #if (holding less than 2 contagious) and (holding less than or equal to 10 non contag) and (patient is not picked up yet):
                    #pick up patient
                    #remove patient from patient list
                    temp_pat_list = copy.deepcopy(self.patient_locations_C)
                    temp_pat_list.remove((row, col))
                    return state(parking_spot=self.parking_spot, parent=self, curr_spot = (row, col), energy_left=self.energy_left - 1, energy_used=self.energy_used + 1, holding_C=self.holding_C+1, holding_N=self.holding_N, patients_dropped_off=self.patients_dropped_off, patient_locations_C=temp_pat_list, patient_locations_N= self.patient_locations_N)
                
                #do not pick up patient, go to spot
                return self.move_no_action(row, col, spot_id)                    
            elif spot_id == 'N':
                if self.holding_C == 0 and self.holding_N < 10 and (row, col) in self.patient_locations_N:
                    #if havent picked up any contagious and we have a spot and havent picked them up yet:
                    #pick up patient + remove from list
                    temp_pat_list = copy.deepcopy(self.patient_locations_N)
                    temp_pat_list.remove((row, col))
                    return state(parking_spot=self.parking_spot, parent=self, curr_spot = (row, col), energy_left=self.energy_left - 1, energy_used=self.energy_used + 1, holding_C=self.holding_C, holding_N=self.holding_N+1, patients_dropped_off=self.patients_dropped_off, patient_locations_C=self.patient_locations_C, patient_locations_N=temp_pat_list)
                
                #do not pick up patient, go to spot
                return self.move_no_action(row, col, spot_id)   
            
            return self.move_no_action(row, col, spot_id)                 
        elif spot_id == 'P':
            #parking recharge is facilitated in the move_no_action function
            return self.move_no_action(row, col, spot_id) 
                           
        return None #not enough energy
    
    def move_left(self, lot_map):
        '''
        Action for moving left
        May return none if not possible
        '''
        row, col = self.curr_spot
        new_spot_id = lot_map[row, col - 1]
        if new_spot_id == 'X' or self.energy_left == 0 or row < 0 or col - 1 < 0:
            #if no energy or X spot
            return None

        #if we can go, this function DECIDES what actions to take in the spot
        return self.decide_state(row, col - 1, new_spot_id)


    def move_right(self, lot_map):
        '''
        Action for moving right
        May return none if not possible
        '''
        row, col = self.curr_spot
        try:
            new_spot_id = lot_map[row][col + 1]
        except IndexError:
            return None
        if new_spot_id == 'X' or self.energy_left == 0 or row < 0 or col + 1 < 0:
            #if no energy or X spot
            return None
        
        return self.decide_state(row, col + 1, new_spot_id)

    def move_down(self, lot_map):
        '''
        Action for moving down
        May return none if not possible
        '''
        row, col = self.curr_spot
        new_spot_id = lot_map[row - 1][col]
        
        
        if new_spot_id == 'X' or self.energy_left == 0 or row - 1 < 0 or col < 0:
            #if no energy or X spot
            return None
        
        if new_spot_id == 'X' or self.energy_left == 0:
            return None 

        return self.decide_state(row - 1, col, new_spot_id)

    def move_up(self, lot_map):
        '''
        Action for moving up
        May return none if not possible
        '''
        row, col = self.curr_spot
        try:
            new_spot_id = lot_map[row + 1][col]
        except IndexError: 
            return None
        
        if new_spot_id == 'X' or self.energy_left == 0 or row + 1 < 0 or col < 0:
            #if no energy or X spot
            return None
        
        if new_spot_id == 'X' or self.energy_left == 0:
            return None
        
        return self.decide_state(row + 1, col, new_spot_id)


    def generate_successors(self, lot_map):
        '''
        Generates all not-none successors of a node
        '''
        l = [self.move_left(lot_map), self.move_down(lot_map), self.move_right(lot_map), self.move_up(lot_map)]
        return [x for x in l if x]

    def print_successors(self, lot_map):
        '''
        Print successors
        '''
        for successor in self.generate_successors(lot_map):
            print(successor)

    def manhattan_distance(self, p1, p2):
        return abs((p1[0] - p2[0])) + abs(p1[1] - p2[1])

    def euclidean_distance(self, p1, p2):
        return int(((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** 0.5)

    def h1_P(self):
        '''
        True if we are looking for parking spot
        '''
        return len(self.patient_locations_C + self.patient_locations_N) == 0 and self.holding_C + self.holding_N == 0

    def heuristic_one(self, CC_locs, CN_locs, P_spot):
        '''
        Simulates the  path to each patient and dropping them off
        Relaxes X constraints
        '''
        if self.h1_P():
            return self.manhattan_distance(self.curr_spot, P_spot)
        else:
            curr_heuristic = 0
            curr_fake_spot = copy.deepcopy(self.curr_spot)
            list_N = copy.deepcopy(self.patient_locations_N)
            list_C = copy.deepcopy(self.patient_locations_C)
            fake_holding_c = copy.deepcopy(self.holding_C)
            fake_holding_n = copy.deepcopy(self.holding_N)        

        while not len(list_N + list_C) == 0 or not fake_holding_c + fake_holding_n == 0:
            while len(list_N) != 0 and fake_holding_c == 0:
                dists = [self.manhattan_distance(patient, curr_fake_spot) for patient in list_N + list_C]
                min_dist = min(dists)
                i = dists.index(min_dist)
                if i < len(list_N):
                    curr_fake_spot = list_N[i]
                    list_N.pop(i)
                    fake_holding_n+=1
                else:
                    curr_fake_spot = list_C[i - len(list_N)]
                    list_C.pop(i - len(list_N))
                    fake_holding_c+=1
                curr_heuristic+=min_dist

            while len(list_C) != 0 and fake_holding_c < 2:
                dists = [self.manhattan_distance(patient_C, curr_fake_spot) for patient_C in list_C]
                min_dist = min(dists)
                i = dists.index(min_dist)
                curr_fake_spot = list_C[i]
                list_C.pop(i)
                fake_holding_c+=1
                curr_heuristic+=min_dist

            curr_heuristic+=min(self.manhattan_distance(curr_fake_spot, CC) for CC in CC_locs)
            fake_holding_c = 0
            curr_heuristic+=min(self.manhattan_distance(CC_locs[0], CN) for CN in CN_locs)
            fake_holding_n = 0
            curr_fake_spot = CN_locs[0]


        curr_heuristic+=self.manhattan_distance(curr_fake_spot, P_spot)
        return curr_heuristic



    def heuristic_two(self, CC_locs, CN_locs, P_spot, debug=False):
        '''
        Simulates the  path to each patient and dropping them off
        Relaxes X constraints
        '''
        if self.h1_P():
            return self.manhattan_distance(self.curr_spot, P_spot)
        else:
            curr_heuristic = 0
            curr_fake_spot = copy.deepcopy(self.curr_spot)
            list_N = copy.deepcopy(self.patient_locations_N)
            list_C = copy.deepcopy(self.patient_locations_C)
            fake_holding_c = copy.deepcopy(self.holding_C)
            fake_holding_n = copy.deepcopy(self.holding_N)   

            if debug == True: print(self.parent) 
            # if self.parent.holding_C == 0 and self.curr_spot in self.parent.patient_locations_C:
            #     curr_heuristic+=kruskal(list_N + [CN_locs[0]])   

        while not len(list_N + list_C) == 0 or not fake_holding_c + fake_holding_n == 0:
            while len(list_N) != 0 and fake_holding_c == 0 and (self.holding_N < 8 or (len(list_C) == 0 and fake_holding_c == 0)):
                dists = [self.manhattan_distance(patient, curr_fake_spot) for patient in list_N + list_C]
                min_dist = min(dists)
                i = dists.index(min_dist)
                if i < len(list_N):
                    curr_fake_spot = list_N[i]
                    list_N.pop(i)
                    fake_holding_n+=1
                else:
                    curr_fake_spot = list_C[i - len(list_N)]
                    list_C.pop(i - len(list_N))
                    fake_holding_c+=1
                curr_heuristic+=min_dist

            while len(list_C) != 0 and fake_holding_c < 2:
                dists = [self.manhattan_distance(patient_C, curr_fake_spot) for patient_C in list_C]
                min_dist = min(dists)
                i = dists.index(min_dist)
                curr_fake_spot = list_C[i]
                list_C.pop(i)
                fake_holding_c+=1
                curr_heuristic+=min_dist

            curr_heuristic+=min(self.manhattan_distance(curr_fake_spot, CC) for CC in CC_locs)
            fake_holding_c = 0
            curr_heuristic+=min(self.manhattan_distance(CC_locs[0], CN) for CN in CN_locs)
            fake_holding_n = 0
            curr_fake_spot = CN_locs[0]


        curr_heuristic+=self.manhattan_distance(curr_fake_spot, P_spot)
        return curr_heuristic
 
    def heuristic(self, chosen_heuristic, CC_locs, CN_locs, P_spot, init_num_patients):
        '''
        Chooses the heuristic based on the user.
        '''
        if chosen_heuristic == '1':
            return self.heuristic_one(CC_locs, CN_locs, P_spot)
        elif chosen_heuristic == '2':
            return self.heuristic_two(CC_locs, CN_locs, P_spot)
        
        print(chosen_heuristic)
        print('Error: requested nonexistent heuristic')
        sys.exit(1)

