DESTINATION=src/generated
REQ_ARGS=1
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
     1 :  To compile file containing C code
   possible flags:
    -h :  Show this help message"
  exit 0
fi




if [ "$#" != ${REQ_ARGS} ];
 then
    echo Incorrect positional argument count: expected ${REQ_ARGS} but got "$#";
    exit 1;
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
    input_files="$(find Input/tests/ -name "*.txt")"
    for file in $input_files; do
      echo "Calling main.py ${file}"
      python3 main.py "$file"
    done
  else
    python3 main.py "$1"
  fi

  exit 0
fi

echo "ERROR: could not find ANTLR generated files"
exit 1
