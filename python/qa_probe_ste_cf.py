#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2015
# Pablo Belzarena <belza@fing.edu.uy>, Gabriel Gomez,  Victor Gonzalez-Barbone, Pablo Flores Guridi, Federico Larroca. 
# ARTES Group
# http://iie.fing.edu.uy/investigacion/grupos/artes/ingles/index.php3
# Instituto de Ingenieria Electrica, Facultad de Ingenieria,
# Universidad de la Republica, Uruguay.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

#
# SYSTEM TARGET ERROR - STE TEST
# For each of the dim_constellation symbol points calculate the distance d_di between
# the theoretical symbol point and the corresponding mean point of the cloud of this
# symbol point. d_di is called Target Error Vector (TEV).This vector indicates the presence of distortions like Carrier Suppression, Amplitude Imbalance, Quadrature Error and may be other non-linear distortions.
# We define the STE as the average of abs(d_di) over the constellation points : sum_{i=0}^{dim_constellation-1}(abs(d_di[i]))/d_dim_constellation
# We define the System Target Error Mean STEM as the STE normalized to the average Tx power STE/tx_power
# We define the System Target Error Deviation as the standard deviation over the constellation points: STED = sqrt(sum_{i=0}^{dim_constellation-1}abs(d_di[i])/d_dim_constellation/tx_power^2- STEM^2) 
# Averaging of the d_di vector is implemented with a first order IIR filter with parameter d_alpha
# This test analize two different types of distorsions: Carrier Suppression Error (global traslation of the constellation) and Amplitud Imbalance Error ( expansion or contraction of the constellation)
# We compare the STE,STEM, STED theoretical values for each distorsion with the probe_ste estimation of these values.

from gnuradio import gr, gr_unittest
from gnuradio import blocks
import mer as mer
import numpy as np
class qa_probe_ste_cf (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
      	# to test a constant complex distorsion added to the symbols (a carrier suppression error)
	# Each vector has all constellation values
	number_of_vectors = 1000
	dim_constellation = 16
	# real and imaginary part of the distorsion added to the symbols
	distorsion_real = 0.1
	distorsion_imag =0.15
	# call the probe_mer constructor with the symbol table and alpha value for averaging
 	self.mer_probe_ste_cf_0 = mer.probe_ste_cf((0.9487+0.9487j,0.9487+0.3162j, 0.3162+0.9487j, 0.3162 +0.3162j,0.9487-0.9487j,0.9487- 0.3162j, 0.3162-0.9487j, 0.3162- 0.3162j,-0.9487+0.9487j,-0.9487+ 0.3162j,- 0.3162+0.9487j,- 0.3162+ 0.3162j,-0.9487-0.9487j,-0.9487- 0.3162j,-0.3162-0.9487j,-0.3162- 0.3162j),0.005)
        #source data to test is a vector of the cosntellation table * number_of_vectors
        src_data = (0.9487+0.9487j,0.9487+0.3162j, 0.3162+0.9487j, 0.3162 +0.3162j,0.9487-0.9487j,0.9487- 0.3162j, 0.3162-0.9487j, 0.3162- 0.3162j,-0.9487+0.9487j,-0.9487+ 0.3162j,- 0.3162+0.9487j,- 0.3162+ 0.3162j,-0.9487-0.9487j,-0.9487- 0.3162j,-0.3162-0.9487j,-0.3162- 0.3162j)*number_of_vectors
	# Add the aditive distorsion to the source data
	src_data = [x+distorsion_real+distorsion_imag*(1j) for x in src_data]
	# create a vector source with the source data and three vector sink blocks to receive the STE,STEM and STED values
        self.src = blocks.vector_source_c(src_data,False)
	self.dst0 = blocks.vector_sink_f()
        self.dst1 = blocks.vector_sink_f()
	self.dst2 = blocks.vector_sink_f()
	#Connect the blocks
        self.tb.connect((self.src, 0), (self.mer_probe_ste_cf_0, 0))    
        self.tb.connect((self.mer_probe_ste_cf_0, 0),(self.dst0, 0))    
        self.tb.connect((self.mer_probe_ste_cf_0, 1),(self.dst1, 0))    
        self.tb.connect((self.mer_probe_ste_cf_0, 2),(self.dst2, 0))    
	self.tb.run ()   
	# The STE,STEM and STED are the average of the last values of received in each destination vector	
	result_data1 = np.mean(self.dst0.data()[number_of_vectors*dim_constellation-dim_constellation:number_of_vectors*dim_constellation])
	print "result = ", result_data1
	result_data2 = np.mean(self.dst1.data()[number_of_vectors*dim_constellation-dim_constellation:number_of_vectors*dim_constellation])
	result_data3 = np.mean(self.dst2.data()[number_of_vectors*dim_constellation-dim_constellation:number_of_vectors*dim_constellation])
	#Calculate the theoretical STE,STEM and STED from the distorsion values	
	ste = np.sqrt(distorsion_real*distorsion_real+distorsion_imag*distorsion_imag)
	expected_result1 = ste
	print " expected result = ",expected_result1
	# as the Tx power is 1 the STEM = STE
	expected_result2 = ste
	# in this case ( add a cosntant to all points) there is not desviation along the constellation points
	error2 = 0.0    
	expected_result3 = error2
	self.assertLessEqual(abs((result_data1-expected_result1)/expected_result1), 0.001 )
	self.assertLessEqual(abs((result_data2-expected_result2)/expected_result2), 0.001 )
	self.assertLessEqual(abs(result_data3-expected_result3), 0.005 )

    def test_002_t (self):
	#to test a  multiplicative distosion to the symbols ( a typical Amplitude Imbalance Error)
	# Each vector has all constellation values
	number_of_vectors = 1000
	dim_constellation = 16
	# real and imaginary part of the distorsion that will multiply each symbols
	distorsion_real = 1.122
	distorsion_imag = 1.13
	# call the probe_mer constructor with the symbol table and alpha value for averaging
 	self.mer_probe_ste_cf_0 = mer.probe_ste_cf((0.9487+0.9487j,0.9487+0.3162j, 0.3162+0.9487j, 0.3162 +0.3162j,0.9487-0.9487j,0.9487- 0.3162j, 0.3162-0.9487j, 0.3162- 0.3162j,-0.9487+0.9487j,-0.9487+ 0.3162j,- 0.3162+0.9487j,- 0.3162+ 0.3162j,-0.9487-0.9487j,-0.9487- 0.3162j,-0.3162-0.9487j,-0.3162- 0.3162j),0.005)
        #source data to test is a vector of the cosntellation table * number_of_vectors
        src_const = (0.9487+0.9487j,0.9487+0.3162j, 0.3162+0.9487j, 0.3162 +0.3162j,0.9487-0.9487j,0.9487- 0.3162j, 0.3162-0.9487j, 0.3162- 0.3162j,-0.9487+0.9487j,-0.9487+ 0.3162j,- 0.3162+0.9487j,- 0.3162+ 0.3162j,-0.9487-0.9487j,-0.9487- 0.3162j,-0.3162-0.9487j,-0.3162- 0.3162j)*number_of_vectors
	#Multiply by the distorsion the source data
	src_data = [x.real*distorsion_real+x.imag * distorsion_imag*(1j) for x in src_const]
	# create a vector source with the source data and three vector sink blocks to receive the STE,STEM and STED values
        self.src = blocks.vector_source_c(src_data,False)
	self.dst0 = blocks.vector_sink_f()
        self.dst1 = blocks.vector_sink_f()
	self.dst2 = blocks.vector_sink_f()
	#Connect the blocks
        self.tb.connect((self.src, 0), (self.mer_probe_ste_cf_0, 0))    
        self.tb.connect((self.mer_probe_ste_cf_0, 0),(self.dst0, 0))    
        self.tb.connect((self.mer_probe_ste_cf_0, 1),(self.dst1, 0))    
        self.tb.connect((self.mer_probe_ste_cf_0, 2),(self.dst2, 0))   
	self.tb.run ()   
	# The STE,STEM and STED are the average of the last values of received in each destination vector	
	result_data1 = np.mean(self.dst0.data()[number_of_vectors*dim_constellation-dim_constellation:number_of_vectors*dim_constellation])
	print "result = ", result_data1
	result_data2 = np.mean(self.dst1.data()[number_of_vectors*dim_constellation-dim_constellation:number_of_vectors*dim_constellation])
	result_data3 = np.mean(self.dst2.data()[number_of_vectors*dim_constellation-dim_constellation:number_of_vectors*dim_constellation])
	error1 = np.sum(   np.sqrt( np.real(src_const)*np.real(src_const)*(distorsion_real-1)*(distorsion_real-1) + np.imag(src_const)*np.imag(src_const) * (distorsion_imag-1)*(distorsion_imag-1)))    
	#Calculate the theoretical STE,STEM and STED from the distorsion values		
	ste = error1/dim_constellation/number_of_vectors;
	expected_result1 = ste
	print " expected result = ",expected_result1
	# as the Tx power is 1 the STEM = STE
	expected_result2 = ste
	# Theorical sted
	error2 = np.sqrt(   np.sum( np.real(src_const)*np.real(src_const)*(distorsion_real-1)*(distorsion_real-1) + np.imag(src_const)*np.imag(src_const) * (distorsion_imag-1)*(distorsion_imag-1))/dim_constellation/number_of_vectors - ste*ste )    
	expected_result3 = error2
	self.assertLessEqual(abs((result_data1-expected_result1)/expected_result1), 0.001 )
	self.assertLessEqual(abs((result_data2-expected_result2)/expected_result2), 0.001 )
	self.assertLessEqual(abs((result_data3-expected_result3)/expected_result3), 0.001 )

if __name__ == '__main__':
    gr_unittest.run(qa_probe_ste_cf, "qa_probe_ste_cf.xml")
