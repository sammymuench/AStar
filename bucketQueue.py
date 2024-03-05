import sys
import time
import numpy as np
import copy

'''
Implemented bucket queue class.
'''
class bucket:
    def __init__(self):
        '''
        Empty list
        '''
        self.buckets = []

    def addAt(self, item, index):
        '''
        Adds at bucket index
        '''
        # Extend the list with None (or a default value) until it reaches the target index
        while len(self.buckets) <= index:
            self.buckets.append(None)

        # Insert the new element at the target index
        if not self.buckets[index]:
            #create a new vector inside a bucket that was previously none
            self.buckets[index] = [item]
        else:
            #
            self.buckets[index].append(item)

    def popFront(self):
        '''
        Pops the first node of the bucket
        '''
        #returns front index of popFront
        i = 0
        while i < len(self.buckets):
            if self.buckets[i]:
                node = self.buckets[i][0]
                self.buckets[i].pop(0)
                if self.buckets[i] == []: self.buckets[i] = None
                return node
            i+=1
        
        print('Error: tried to pop from empty list')
        sys.exit(1)

    def __str__(self):
        return str([b.__str__() for b in self.buckets])

    def isEmpty(self):
        '''
        Input: self
        Output: bool - True if empty, False if not empty
        '''
        i = 0
        while i < len(self.buckets):
            if self.buckets[i] != None or self.buckets[i] != []: return False
            i+=1

        return True
    
    def in_list(self, element, i):
        '''
        Input: self, element: state class, i: index where the state may be
        Output: bool, True if element is in bucket, False otherwise
        '''
        return element in self.buckets[i]