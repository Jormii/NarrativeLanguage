SOURCE_DIR="../src/"
MAKE_DIR="./"

# Compile source
cwd=$(pwd)
cd $MAKE_DIR
make -B
cd $cwd

# Build libray
OBJECT_FILES=$(find $SOURCE_DIR -name \*.o)
ar -rc cyoa.a $OBJECT_FILES
rm -f $OBJECT_FILES
