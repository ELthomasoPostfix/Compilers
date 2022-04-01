DESTINATION=src/generated
REQ_ARGS=1
h_flag=false


while getopts 'h' flag; do
  case "${flag}" in
    h) h_flag=true ;;
    *) ;;
  esac
done

if [ "$h_flag" = true ]
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
if [ $FILE_COUNT -ne 1 ]
then
  echo "ANTLR generated files not found"
  chmod +x generate.sh
  ./generate.sh
fi

FILE_COUNT=$(find $DESTINATION -name  "*Parser.py" | wc -l)
if [ $FILE_COUNT -eq 1 ]
then
  echo "Calling main.py"
  python3 main.py $1
  exit 0
fi

echo "ERROR: could not find ANTLR generated files"
exit 1
