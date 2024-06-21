import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyNE-probe", # Replace with your own username
    version="1.0.0",
    author="Adam Micolich",
    author_email="adam.micolich@gmail.com",
    description="A simple Python 3 interface for controlling electronic measurement instruments and scripting measurement sweeps on the probe station.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AdMico/PyNE-probe",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,  #this should tell the package to include the non-python files defined in MANIFEST.in
    python_requires='>=3.11',
    install_requires = ['numpy','cycler','kiwisolver','matplotlib','nidaqmx','pandas','Pillow','scipy','pyvisa','pytz','pyparsing','python-dateutil','six']
)



