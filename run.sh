DESTINATION=src/generated/
DEFAULT_INPUT_DIR=Input/tests/
help_flag=false
all_flag=false


while getopts 'ha' flag; do
  case "${flag}" in
    h) help_flag=true ;;
    a) all_flag=true ;;
    *) ;;
  esac
done

if [ "$help_flag" = true ]
then
  echo "Compile the specified file(s).
   positional arguments:
          Treat all positional arguments as to compile files containing C code
   possible flags:
    -h :  Show this help message
    -a :  Compile all files in the directory ${DEFAULT_INPUT_DIR}"
  exit 0
fi






chmod +x ensure_destination.sh
./ensure_destination.sh -d $DESTINATION

FILE_COUNT=$(find $DESTINATION -name "*Parser.py" | wc -l)
if [ "$FILE_COUNT" -ne 1 ]
then
  echo "ANTLR generated files not found"
  chmod +x build.sh
  ./build.sh
fi

FILE_COUNT=$(find $DESTINATION -name  "*Parser.py" | wc -l)
if [ "$FILE_COUNT" -eq 1 ]
then
  if [ "$all_flag" = true ]
  then
    input_files="$(find $DEFAULT_INPUT_DIR -name "*.txt")"
    echo "processing "$(echo $input_files | wc -w)" files"
    for file in $input_files; do
      echo "Calling main.py ${file}"
      python3 main.py "$file"
    done
  else
    echo "processing $# files"
    pos_arg=$1
    for pos_arg ; do
      echo "Calling main.py ${pos_arg}"
      python3 main.py "$pos_arg"
    done
  fi

  exit 0
fi

echo "ERROR: could not find ANTLR generated files"
exit 1
