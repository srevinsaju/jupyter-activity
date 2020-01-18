echo Installing Jupyter from offline files.
JUPYTER_DIST=./jupyter-bundle
if test -f "$JUPYTER_DIST"; then
    echo "$JUPYTER_DIST Exists, installing..."
    python3 -m pip install ./jupyter-bundle/* --user
else
  echo jupyter-bundle doesnt exist. Please download jupyter-packages from a PC with internet connection.
  echo and put it in a jupyter-bundle in the current working directory.
fi