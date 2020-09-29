export PYTHON_INCLUDE_DIRS=$(python3 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())")  \
export PYTHON_LIBRARIES=$(python3 -c "import distutils.sysconfig as sysconfig; print(sysconfig.get_config_var('LIBDIR'))")
export python3include=$(python3 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())")  \
export python3lib=$(python3 -c "import distutils.sysconfig as sysconfig; print(sysconfig.get_config_var('LIBDIR'))")
