# A Rule Monitor for Business Process Management

Python 3

Usage: python run_experiment.py [path to file containing list of monitor specs] [name of output file]

Example:

python run_experiment.py 2-rule-monitor.txt demo-output

where

2-rule-monitor.txt has the following contents:

first-rule.txt
second-rule.txt

and 

first-rule.txt has the following contents:
Rule 
ReadThenFAQ
if
read(support a, value d, class b, name c)@x
then
check_faq(support a, name c)@z
x <= z
x+100 >= z
end

second-rule.txt has the following contents;
Rule 
ReadThenOpenTrust
if
read(support a, value d, class b, name c)@x
then
open_trust(support a, name c)@z
x <= z
x+100 >= z
end
