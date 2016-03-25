# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 14:44:30 2015

@author: m131199
"""
import os
import csv
os.chdir('/home/m131199/Desktop')
with open('zet.csv', 'a') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
    spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])
    spamwriter.writerow(['zeynettin'])
    
    
    
with open('zet.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
#        print ', '.join(row)
        print row
        
        
        