<img src=https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png width=25%>

# Jupyter Activity (beta)
>**Jupyter Notebook** formerly IPython Notebooks) is a web-based 
interactive computational environment for creating Jupyter 
notebook documents. The "notebook" term can colloquially make
reference to many different entities, mainly the Jupyter web
application, Jupyter Python web server, or Jupyter document
format depending on context. A Jupyter Notebook document is
a JSON document, following a versioned schema, and containing 
an ordered list of input/output cells which can contain code, 
text (using Markdown), mathematics, plots and rich media, 
usually ending with the ".ipynb" extension. ~ Wikipedia

This Activity features a Jupyter Labs for students in the 
Sugar theme and its journal contols.

Jupyter is a leading Python Interactive Console, and would be
an enriching beginner to professional coding experience for 
the three popular languages Python, Julia and Ruby. 

<img width=25% src=https://camo.githubusercontent.com/fc57a9f9fcbb2ee30d7aaf1fef09ae50dc27f67f/68747470733a2f2f63646e2e6f7265696c6c797374617469632e636f6d2f656e2f6173736574732f312f6576656e742f3237312f6a75706e79323031375f706f77657265645f62795f6c6f676f2e706e67>

## Installing

* On desktops with internet, the dependencies, will be
be automatically installed.

### Offline Download
Jupyter needs `jupyter`, `jupyterlabs` and `notebooks` to work
The jupyter activity on launch automatically downloads the 
required dependencies online. 
It is possible to install jupyter on a computer without
internet access. 

#### Downloading Jupyter-Bundle
On a computer with internet access, execute:
```buildoutcfg
./download-jupyter.sh
```
You will notice, the files have been created in a `jupyter-bundle
` directory.

#### Instaling Jupyter
Now, copy these files to a computer without internet
and then execute:
```buildoutcfg
./install-offline-jupyter.sh
```
And now jupyter should have been installed successfully.
You can test it by 
```
jupyter-lab --version
```

## License
```buildoutcfg
MIT License

Copyright (c) 2020 Srevin Saju

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```
