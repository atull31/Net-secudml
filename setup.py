#The setup.py file is an essential part of packaging and 
#distributing python projs. it is used by setup tool
#(or distutils in older python versions) to define the config
#of the project such as its metadata, dependencies and more.


from setuptools import find_packages,setup  #(considers the folder containing __init__.py as packages)
from typing import List


def get_requirements()->List[str]:
    """
    This function will return list of requirements
    
    """
    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt','r') as file:
            lines = file.readlines() #read lines from file
            for line in lines: #process each line
                requirement = line.strip()
                if requirement and requirement != '-e .':#ignore empty lines and -e .
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("Requirements file not found")

    return requirement_lst

setup(
    name="NetworkSecurity",
    version="0.0.1",
    author="Atul Kumar",
    author_email="imatul5899@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)  