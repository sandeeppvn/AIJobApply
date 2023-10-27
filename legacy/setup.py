from setuptools import find_packages, setup

setup(
    name="AIJobApply",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "ConfigParser==6.0.0",
        "mock==5.1.0",
        "openai==0.27.4",
        "PyPDF2==3.0.1",
        "pytest==7.4.3",
        "python-dotenv==1.0.0",
        "tqdm==4.65.0",
        "click==8.1.3",
        "requests==2.28.2",
    ],
    entry_points={
        "console_scripts": ["aijobapply = src.main:aijobapply_cli"],
    },
    author="Sandeep Polavarapu",
    author_email="sandeeppvn@gmail.com",
    description="Package to apply for jobs automatically and send emails",
    url="https://github.com/sandeeppvn/AIJobApply",
)
