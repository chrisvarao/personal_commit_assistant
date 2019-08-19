import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="personal_commit_assistant",
    version="0.0.17",
    author="Chris Rao",
    author_email="chris.va.rao@gmail.com",
    description="Keeps your commits up to your standards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chrisvarao/personal_commit_assistant",
    install_requires=["pick>=0.6.4", "GitPython>=2.1.11"],
    packages=setuptools.find_packages(),
    console_scripts={
        "personal_commit_assistant=personal_commit_assistant"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
