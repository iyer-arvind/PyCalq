PyCalq
======

Pycalq is a engineering calculators with units support.
It is basically a non linear simultaneous equation solver.

------

Input
-----

A view of how the equations can be solved gives an idea of the usefulness of the calculator.
A typical input file has 2 sections, the equations section and a variables section.

Lets solve a simple problem of kinematics. 

>I need to travel a distance of 15, with an initial speed of 0 and a final speed of 1. What will be my acceleration, and what will be the time I take to reach the destination?

Well we all know that the equation of kinematics are
> S = u*t + 0.5 * a * t * t  and
> v = u + a*t

So this problem can be described as:

> kinematics.txt

    S = u*t + 0.5*a*t*t                                                            
    v = u + a*t                                                                    
                                                                                   
                                                                                   
    ::                                                                             
    S := 15.0                                                                      
    u := 0.0                                                                       
    v := 1.0                                                                       
                                                                                   
    a = 0.0                                                                        
    t = 10.0

The calculator can be invoked with 

    $ pycalq kinematics.txt
    -----------
		a   0.0333333
		t  30
    ----------

Which immediately tells that the acceleration is 0.0333 and it takes 30 time units.
Note that the equations were not explicit in acceleration or time.

A few notes about the input format, 
1) The equation section precedes the variable section and is separated with `::`
2) The parameters are defined with `:=` and are those whose values are not changed
3) Those parameters defined with `=` are the ones which are solved for, the values are used as initial guess

Units
---
PyCalq supports units using pint. Suppose in the above problem, S was in kilometers, v in miles per hour, and t in hours,
we can wrie the input as 


> Kinematics-u.txt

	S = u*t + 0.5*a*t*t                                                            
	v = u + a*t                                                                    
                                                                               
                                                                               
	::                                                                             
	S := 15.0[km]                                                                  
	u := 0.0[m/s]                                                                  
	v := 1.0[mph]                                                                  
	                                                                               
	a = 0.0[m/s/s]                                                                 
	t = 10.0[hours]                                                                

Which gives

	$ pycalq Kinematics-u.txt
  -----------------------------------------
	a  6.661492053333608e-06 meter / second ** 2
	t  18.641135767119685 hour
	-----------------------------------------


