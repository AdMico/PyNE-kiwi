import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyNE-kiwi", # Replace with your own username
    version="1.0.0",
    author="Adam Micolich",
    author_email="adam.micolich@gmail.com",
    description="A simple Python 3 interface for controlling electronic measurement instruments and scripting measurement sweeps at VUW.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AdMico/PyNE-kiwi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,  #this should tell the package to include the non-python files defined in MANIFEST.in
    python_requires='>=3.12',
    install_requires = ['pip','setuptools','wheel','numpy','matplotlib','contourpy','cycler','fonttools','kiwisolver','packaging','pillow','pyparsing','python-dateutil','six','scipy','pyvisa','typing-extensions','visa','certifi','charset-normalizer','idna','requests','urllib3','deprecation','pandas','pytz','tzdata','pandastable','future','numexpr','xlrd','easygui','colorzero','gpiozero','pigpio']
)



